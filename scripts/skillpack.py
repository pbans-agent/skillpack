#!/usr/bin/env python3
"""Skill Pack CLI.

A lightweight, stdlib-first CLI for listing, validating, installing, updating,
checking status, and packaging Git-backed Agent Skills.

Usage:
    python3 scripts/skillpack.py list
    python3 scripts/skillpack.py validate
    python3 scripts/skillpack.py install --scope personal --profile all
    python3 scripts/skillpack.py install --scope project --project-path . --profile all
    python3 scripts/skillpack.py status --scope personal
    python3 scripts/skillpack.py update --scope personal --profile all
    python3 scripts/skillpack.py package --profile all --out dist/skillpack-all.zip
"""

from __future__ import annotations

import argparse
import datetime as _dt
import fnmatch
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import textwrap
import zipfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Tuple


NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SECRET_NAME_RE = re.compile(
    r"(^|/)(\.env($|\.)|id_rsa|id_dsa|id_ecdsa|id_ed25519|.*private.*key.*|.*secret.*|.*token.*|credentials\.json|auth\.json|.*\.pem$|.*\.key$)",
    re.IGNORECASE,
)
MARKER_NAME = ".skillpack-source.json"
LOCK_DIR = Path("~/.skillpacks/installed").expanduser()
DEFAULT_PACK_NAME = "skillpack"


class SkillPackError(Exception):
    """User-facing Skill Pack error."""


@dataclass
class Skill:
    name: str
    path: Path
    frontmatter: Dict[str, Any]
    description: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    hash: str = ""


@dataclass
class ValidationResult:
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not self.errors

    def add_error(self, msg: str) -> None:
        self.errors.append(msg)

    def add_warning(self, msg: str) -> None:
        self.warnings.append(msg)

    def extend(self, other: "ValidationResult") -> None:
        self.errors.extend(other.errors)
        self.warnings.extend(other.warnings)


# ---------------------------------------------------------------------------
# YAML loading — PyYAML when available, minimal fallback otherwise
# ---------------------------------------------------------------------------


def load_yaml_text(text: str) -> Dict[str, Any]:
    """Load a small YAML document.

    Uses PyYAML if installed. Falls back to a minimal parser that supports the
    subset used by this repo: nested maps, scalar lists, inline empty lists,
    quoted strings, and folded/literal block scalars.
    """

    try:  # pragma: no cover - environment-dependent
        import yaml  # type: ignore

        data = yaml.safe_load(text) or {}
        if not isinstance(data, dict):
            raise SkillPackError("YAML document must be a mapping at top level")
        return data
    except ImportError:
        return _simple_yaml_load(text)


def _strip_comment(line: str) -> str:
    """Strip YAML comments unless inside simple quotes."""

    in_single = False
    in_double = False
    out = []
    i = 0
    while i < len(line):
        ch = line[i]
        if ch == "'" and not in_double:
            in_single = not in_single
        elif ch == '"' and not in_single:
            in_double = not in_double
        elif ch == "#" and not in_single and not in_double:
            break
        out.append(ch)
        i += 1
    return "".join(out).rstrip()


def _simple_yaml_load(text: str) -> Dict[str, Any]:
    raw_lines = text.splitlines()
    lines: List[Tuple[int, str]] = []
    i = 0
    while i < len(raw_lines):
        raw = raw_lines[i].rstrip("\n")
        if not raw.strip() or raw.lstrip().startswith("#"):
            i += 1
            continue
        cleaned = _strip_comment(raw)
        if not cleaned.strip():
            i += 1
            continue
        indent = len(cleaned) - len(cleaned.lstrip(" "))
        lines.append((indent, cleaned.strip()))
        i += 1

    def parse_scalar(value: str) -> Any:
        value = value.strip()
        if value in ("", "null", "Null", "NULL", "~"):
            return None
        if value in ("[]",):
            return []
        if value in ("{}",):
            return {}
        if value in ("true", "True", "TRUE"):
            return True
        if value in ("false", "False", "FALSE"):
            return False
        if (value.startswith('"') and value.endswith('"')) or (
            value.startswith("'") and value.endswith("'")
        ):
            return value[1:-1]
        if value.startswith("[") and value.endswith("]"):
            inner = value[1:-1].strip()
            if not inner:
                return []
            return [parse_scalar(part.strip()) for part in inner.split(",")]
        # Keep numbers as strings for manifest/frontmatter stability.
        return value

    def parse_block_scalar(start_index: int, parent_indent: int, style: str) -> Tuple[str, int]:
        block_lines: List[str] = []
        j = start_index
        base_indent: Optional[int] = None
        while j < len(raw_lines):
            raw = raw_lines[j].rstrip("\n")
            if not raw.strip():
                block_lines.append("")
                j += 1
                continue
            indent = len(raw) - len(raw.lstrip(" "))
            if indent <= parent_indent:
                break
            if base_indent is None:
                base_indent = indent
            block_lines.append(raw[base_indent:])
            j += 1
        if style.startswith(">"):  # folded
            return " ".join(line.strip() for line in block_lines).strip(), j
        return "\n".join(block_lines).rstrip(), j

    # For block scalars we need a raw-line parser; the normalized parser below
    # handles the regular nested structures.
    def parse_node(index: int, indent: int) -> Tuple[Any, int]:
        if index >= len(lines):
            return {}, index
        _, first = lines[index]
        if first.startswith("- "):
            return parse_list(index, indent)
        return parse_dict(index, indent)

    def find_raw_line_index(normalized_line: str, occurrence: int) -> int:
        count = 0
        for idx, raw in enumerate(raw_lines):
            if _strip_comment(raw).strip() == normalized_line:
                if count == occurrence:
                    return idx
                count += 1
        return len(raw_lines)

    normalized_occurrences: Dict[str, int] = {}

    def parse_dict(index: int, indent: int) -> Tuple[Dict[str, Any], int]:
        result: Dict[str, Any] = {}
        while index < len(lines):
            curr_indent, content = lines[index]
            if curr_indent < indent:
                break
            if curr_indent > indent:
                raise SkillPackError(f"Unexpected indentation near: {content}")
            if content.startswith("- "):
                break
            if ":" not in content:
                raise SkillPackError(f"Expected key: value line, got: {content}")
            key, value = content.split(":", 1)
            key = key.strip()
            value = value.strip()
            if value in ("|", "|-", "|+", ">", ">-", ">+"):
                occurrence = normalized_occurrences.get(content, 0)
                normalized_occurrences[content] = occurrence + 1
                raw_idx = find_raw_line_index(content, occurrence)
                block_value, raw_next = parse_block_scalar(raw_idx + 1, curr_indent, value)
                result[key] = block_value
                # Convert raw_next back to normalized index.
                consumed_content = set()
                new_index = index + 1
                while new_index < len(lines):
                    raw_line_idx = find_raw_line_index(lines[new_index][1], 0)
                    if raw_line_idx >= raw_next:
                        break
                    # avoid infinite loop on duplicate lines by simple advance
                    line_key = (lines[new_index][0], lines[new_index][1], new_index)
                    if line_key in consumed_content:
                        break
                    consumed_content.add(line_key)
                    new_index += 1
                index = new_index
            elif value == "":
                if index + 1 >= len(lines) or lines[index + 1][0] <= curr_indent:
                    result[key] = None
                    index += 1
                else:
                    child, index = parse_node(index + 1, lines[index + 1][0])
                    result[key] = child
            else:
                result[key] = parse_scalar(value)
                index += 1
        return result, index

    def parse_list(index: int, indent: int) -> Tuple[List[Any], int]:
        result: List[Any] = []
        while index < len(lines):
            curr_indent, content = lines[index]
            if curr_indent < indent:
                break
            if curr_indent > indent:
                raise SkillPackError(f"Unexpected list indentation near: {content}")
            if not content.startswith("- "):
                break
            item = content[2:].strip()
            if item == "":
                if index + 1 >= len(lines) or lines[index + 1][0] <= curr_indent:
                    result.append(None)
                    index += 1
                else:
                    child, index = parse_node(index + 1, lines[index + 1][0])
                    result.append(child)
            elif ":" in item and not item.startswith(('"', "'")):
                key, value = item.split(":", 1)
                result.append({key.strip(): parse_scalar(value.strip())})
                index += 1
            else:
                result.append(parse_scalar(item))
                index += 1
        return result, index

    parsed, next_index = parse_node(0, lines[0][0] if lines else 0)
    if next_index != len(lines):
        raise SkillPackError("Could not parse entire YAML document")
    if not isinstance(parsed, dict):
        raise SkillPackError("YAML document must be a mapping at top level")
    return parsed


def load_yaml_file(path: Path) -> Dict[str, Any]:
    if not path.exists():
        raise SkillPackError(f"YAML file not found: {path}")
    return load_yaml_text(path.read_text(encoding="utf-8"))


# ---------------------------------------------------------------------------
# Repo and Git helpers
# ---------------------------------------------------------------------------


def repo_root() -> Path:
    """Return the repo root based on this script location."""

    return Path(__file__).resolve().parents[1]


def run_git(args: List[str], cwd: Optional[Path] = None, check: bool = False) -> subprocess.CompletedProcess[str]:
    proc = subprocess.run(
        ["git", *args],
        cwd=str(cwd or repo_root()),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if check and proc.returncode != 0:
        raise SkillPackError(proc.stderr.strip() or proc.stdout.strip() or f"git {' '.join(args)} failed")
    return proc


def git_commit() -> str:
    proc = run_git(["rev-parse", "HEAD"])
    if proc.returncode == 0:
        return proc.stdout.strip()
    return "unknown"


def git_remote() -> str:
    proc = run_git(["config", "--get", "remote.origin.url"])
    if proc.returncode == 0 and proc.stdout.strip():
        return proc.stdout.strip()
    return str(repo_root())


def is_git_repo() -> bool:
    proc = run_git(["rev-parse", "--is-inside-work-tree"])
    return proc.returncode == 0 and proc.stdout.strip() == "true"


def git_dirty() -> bool:
    proc = run_git(["status", "--porcelain"])
    return proc.returncode == 0 and bool(proc.stdout.strip())


def git_has_upstream() -> bool:
    proc = run_git(["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{u}"])
    return proc.returncode == 0 and bool(proc.stdout.strip())


# ---------------------------------------------------------------------------
# Skill discovery and validation
# ---------------------------------------------------------------------------


def load_manifest() -> Dict[str, Any]:
    manifest_path = repo_root() / "skillpack.yaml"
    return load_yaml_file(manifest_path)


def skills_root(manifest: Optional[Dict[str, Any]] = None) -> Path:
    manifest = manifest or load_manifest()
    root = manifest.get("skills_root", "skills")
    return repo_root() / str(root)


def parse_frontmatter(skill_md: Path) -> Tuple[Dict[str, Any], str]:
    text = skill_md.read_text(encoding="utf-8")
    if not text.startswith("---"):
        raise SkillPackError(f"{skill_md}: missing YAML frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise SkillPackError(f"{skill_md}: frontmatter must start and end with ---")
    fm_text = parts[1].strip()
    body = parts[2]
    fm = load_yaml_text(fm_text)
    return fm, body


def hash_skill_dir(skill_dir: Path) -> str:
    sha = hashlib.sha256()
    for path in sorted(skill_dir.rglob("*")):
        if path.is_dir():
            continue
        rel = path.relative_to(skill_dir).as_posix()
        if rel == MARKER_NAME or rel.endswith(".pyc") or "__pycache__" in rel.split("/"):
            continue
        sha.update(rel.encode("utf-8"))
        sha.update(b"\0")
        try:
            sha.update(path.read_bytes())
        except FileNotFoundError:
            # Broken symlink or race; include path only.
            pass
        sha.update(b"\0")
    return "sha256:" + sha.hexdigest()


def discover_skills(manifest: Optional[Dict[str, Any]] = None) -> Dict[str, Skill]:
    manifest = manifest or load_manifest()
    root = skills_root(manifest)
    if not root.exists():
        raise SkillPackError(f"skills_root does not exist: {root}")
    skills: Dict[str, Skill] = {}
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        skill_md = child / "SKILL.md"
        if skill_md.exists():
            try:
                fm, _body = parse_frontmatter(skill_md)
            except SkillPackError:
                fm = {}
            name = str(fm.get("name") or child.name)
            description = str(fm.get("description") or "")
            metadata = fm.get("metadata") or {}
            if not isinstance(metadata, dict):
                metadata = {}
            skills[child.name] = Skill(
                name=name,
                path=child,
                frontmatter=fm,
                description=description,
                metadata=metadata,
                hash=hash_skill_dir(child),
            )
    return skills


def validate_manifest(manifest: Dict[str, Any]) -> ValidationResult:
    result = ValidationResult()
    required = ["name", "display_name", "version", "default_profile", "skills_root", "profiles"]
    for key in required:
        if key not in manifest:
            result.add_error(f"manifest: missing required key '{key}'")
    root = skills_root(manifest)
    if not root.exists():
        result.add_error(f"manifest: skills_root does not exist: {root}")
    profiles = manifest.get("profiles")
    if not isinstance(profiles, dict):
        result.add_error("manifest: profiles must be a mapping")
    else:
        default_profile = manifest.get("default_profile")
        if default_profile not in profiles:
            result.add_error(f"manifest: default_profile '{default_profile}' not found in profiles")
        for profile_name, profile in profiles.items():
            if not isinstance(profile, dict):
                result.add_error(f"manifest: profile '{profile_name}' must be a mapping")
                continue
            include = profile.get("include", [])
            exclude = profile.get("exclude", [])
            if not isinstance(include, list):
                result.add_error(f"manifest: profile '{profile_name}' include must be a list")
            if not isinstance(exclude, list):
                result.add_error(f"manifest: profile '{profile_name}' exclude must be a list")
    return result


def is_vague_description(desc: str) -> bool:
    desc_l = desc.lower().strip()
    vague_phrases = {
        "helps with skills",
        "helps with documents",
        "helps with commits",
        "useful skill",
        "does stuff",
        "general helper",
    }
    return desc_l in vague_phrases or desc_l.startswith("helps with ") and len(desc_l) < 40


def markdown_links(text: str) -> Iterable[str]:
    for match in re.finditer(r"\[[^\]]+\]\(([^)]+)\)", text):
        yield match.group(1).strip()


def should_validate_link(link: str) -> bool:
    lower = link.lower()
    return not (
        lower.startswith("http://")
        or lower.startswith("https://")
        or lower.startswith("mailto:")
        or lower.startswith("#")
        or lower.startswith("data:")
    )


def validate_skill(skill_dir: Path) -> ValidationResult:
    result = ValidationResult()
    skill_md = skill_dir / "SKILL.md"
    if not skill_md.exists():
        result.add_error(f"{skill_dir.name}: missing SKILL.md")
        return result

    try:
        fm, body = parse_frontmatter(skill_md)
    except SkillPackError as exc:
        result.add_error(str(exc))
        return result

    name = fm.get("name")
    desc = fm.get("description")
    if not name:
        result.add_error(f"{skill_dir.name}: frontmatter missing 'name'")
    elif name != skill_dir.name:
        result.add_error(f"{skill_dir.name}: frontmatter name '{name}' does not match directory name")
    elif not NAME_RE.match(str(name)):
        result.add_error(f"{skill_dir.name}: name must be lowercase letters/numbers/hyphens only")

    if not desc:
        result.add_error(f"{skill_dir.name}: frontmatter missing 'description'")
    else:
        desc_str = str(desc).strip()
        if len(desc_str) < 40:
            result.add_warning(f"{skill_dir.name}: description is short; include specific trigger contexts")
        if is_vague_description(desc_str):
            result.add_warning(f"{skill_dir.name}: description is vague; say what it does and when to use it")
        if "use when" not in desc_str.lower() and "use as" not in desc_str.lower():
            result.add_warning(f"{skill_dir.name}: description should include 'Use when...' trigger guidance")

    metadata = fm.get("metadata")
    if metadata is not None and not isinstance(metadata, dict):
        result.add_warning(f"{skill_dir.name}: metadata should be a mapping")

    skill_text = skill_md.read_text(encoding="utf-8")
    for link in markdown_links(skill_text):
        if not should_validate_link(link):
            continue
        clean_link = link.split("#", 1)[0]
        if not clean_link:
            continue
        target = (skill_dir / clean_link).resolve()
        try:
            target.relative_to(repo_root())
        except ValueError:
            result.add_warning(f"{skill_dir.name}: link points outside repo: {link}")
            continue
        if not target.exists():
            result.add_error(f"{skill_dir.name}: linked file does not exist: {link}")

    # Secret-looking files and large SKILL.md warning
    if len(skill_text) > 12_000 and not (skill_dir / "references").exists():
        result.add_warning(f"{skill_dir.name}: SKILL.md is large; move details into references/")

    for path in skill_dir.rglob("*"):
        if path.is_dir():
            continue
        rel = path.relative_to(skill_dir).as_posix()
        if SECRET_NAME_RE.search(rel):
            result.add_error(f"{skill_dir.name}: secret-looking file should not be committed: {rel}")

    scripts_dir = skill_dir / "scripts"
    if scripts_dir.exists():
        for script in sorted(scripts_dir.iterdir()):
            if not script.is_file():
                continue
            text = script.read_text(encoding="utf-8", errors="ignore")
            rel = script.relative_to(repo_root()).as_posix()
            if not os.access(script, os.X_OK) and not text.startswith("#!"):
                result.add_warning(f"{skill_dir.name}: script is not executable and has no shebang: {rel}")
            if "--help" not in text and "argparse" not in text and "Usage:" not in text:
                result.add_warning(f"{skill_dir.name}: script should document --help/usage: {rel}")
            if re.search(r"\binput\s*\(", text):
                result.add_warning(f"{skill_dir.name}: script appears interactive (input()); prefer flags/stdin: {rel}")

    evals = skill_dir / "evals" / "evals.json"
    if evals.exists():
        try:
            data = json.loads(evals.read_text(encoding="utf-8"))
            if data.get("skill_name") != skill_dir.name:
                result.add_warning(f"{skill_dir.name}: evals.json skill_name does not match directory")
            if not isinstance(data.get("evals", []), list):
                result.add_warning(f"{skill_dir.name}: evals.json 'evals' should be a list")
        except json.JSONDecodeError as exc:
            result.add_error(f"{skill_dir.name}: evals/evals.json invalid JSON: {exc}")

    return result


def validate_all(selected: Optional[List[str]] = None, quiet: bool = False) -> ValidationResult:
    result = ValidationResult()
    try:
        manifest = load_manifest()
    except Exception as exc:
        result.add_error(f"manifest: {exc}")
        return result

    result.extend(validate_manifest(manifest))

    root = skills_root(manifest)
    if root.exists():
        skills = discover_skills(manifest)
        if not skills:
            result.add_warning("no skills discovered")
        names = selected or sorted(skills.keys())
        for name in names:
            skill = skills.get(name)
            if not skill:
                result.add_error(f"selected skill not found: {name}")
                continue
            result.extend(validate_skill(skill.path))

        # Validate profiles resolve.
        profiles = manifest.get("profiles", {})
        if isinstance(profiles, dict):
            for profile_name, profile in profiles.items():
                try:
                    resolved = resolve_profile(profile_name, manifest, skills)
                    allow_empty = bool(profile.get("allow_empty")) if isinstance(profile, dict) else False
                    if not resolved and not allow_empty:
                        result.add_warning(f"profile '{profile_name}' resolves to zero skills")
                except SkillPackError as exc:
                    result.add_error(str(exc))

    if not quiet:
        print_validation(result)
    return result


def print_validation(result: ValidationResult) -> None:
    if result.errors:
        print("Validation errors:")
        for err in result.errors:
            print(f"  ✗ {err}")
    if result.warnings:
        print("Validation warnings:")
        for warn in result.warnings:
            print(f"  ⚠ {warn}")
    if result.ok:
        if result.warnings:
            print(f"Validation passed with {len(result.warnings)} warning(s).")
        else:
            print("Validation passed.")
    else:
        print(f"Validation failed with {len(result.errors)} error(s), {len(result.warnings)} warning(s).")


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------


def resolve_profile(
    profile_name: str,
    manifest: Optional[Dict[str, Any]] = None,
    skills: Optional[Dict[str, Skill]] = None,
) -> List[str]:
    manifest = manifest or load_manifest()
    skills = skills or discover_skills(manifest)
    profiles = manifest.get("profiles", {})
    if profile_name not in profiles:
        raise SkillPackError(f"profile not found: {profile_name}")
    profile = profiles[profile_name] or {}
    include = profile.get("include", []) or []
    exclude = profile.get("exclude", []) or []
    if not isinstance(include, list) or not isinstance(exclude, list):
        raise SkillPackError(f"profile '{profile_name}' include/exclude must be lists")

    selected: set[str] = set()
    for pattern in include:
        pattern = str(pattern)
        if pattern == "*":
            selected.update(skills.keys())
        else:
            matched = [name for name in skills if fnmatch.fnmatch(name, pattern)]
            selected.update(matched)

    for pattern in exclude:
        pattern = str(pattern)
        for name in list(selected):
            if fnmatch.fnmatch(name, pattern):
                selected.remove(name)

    return sorted(selected)


# ---------------------------------------------------------------------------
# Install, status, update, package
# ---------------------------------------------------------------------------


def utc_now() -> str:
    return _dt.datetime.now(tz=_dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def target_for_scope(scope: str, project_path: Optional[str], manifest: Dict[str, Any]) -> Tuple[Path, Path]:
    targets = (((manifest.get("install_targets") or {}).get("claude_code") or {}))
    pack_name = manifest.get("name", DEFAULT_PACK_NAME)
    if scope == "personal":
        target = Path(str(targets.get("personal_path", "~/.claude/skills"))).expanduser()
        lock = LOCK_DIR / f"{pack_name}.lock.json"
    elif scope == "project":
        if not project_path:
            project_path = "."
        project = Path(project_path).expanduser().resolve()
        target = project / str(targets.get("project_path", ".claude/skills"))
        lock = project / ".claude" / "skillpack.lock.json"
    else:
        raise SkillPackError(f"unknown scope: {scope}")
    return target, lock


def read_marker(skill_path: Path) -> Optional[Dict[str, Any]]:
    marker = skill_path / MARKER_NAME
    if not marker.exists():
        return None
    try:
        return json.loads(marker.read_text(encoding="utf-8"))
    except Exception:
        return None


def write_marker(skill_path: Path, marker: Dict[str, Any]) -> None:
    (skill_path / MARKER_NAME).write_text(json.dumps(marker, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def copy_skill(src: Path, dst: Path) -> None:
    def ignore(_dir: str, names: List[str]) -> set[str]:
        ignored = {"__pycache__", ".pytest_cache", MARKER_NAME}
        return {name for name in names if name in ignored or name.endswith(".pyc")}

    shutil.copytree(src, dst, ignore=ignore)


def symlink_skill(src: Path, dst: Path) -> None:
    os.symlink(src.resolve(), dst)


def install_skills(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    skills = discover_skills(manifest)
    profile = args.profile or manifest.get("default_profile", "all")
    selected = resolve_profile(profile, manifest, skills)
    mode = args.mode or (((manifest.get("defaults") or {}).get("install_mode")) or "copy")
    if mode not in ("copy", "symlink"):
        raise SkillPackError("--mode must be 'copy' or 'symlink'")

    if (manifest.get("defaults") or {}).get("require_validation", True) and not args.skip_validation:
        validation = validate_all(selected=selected, quiet=True)
        if not validation.ok:
            print_validation(validation)
            raise SkillPackError("refusing to install because validation failed")
        if validation.warnings and not args.quiet:
            print(f"Validation passed with {len(validation.warnings)} warning(s); continuing.")

    target, lock_path = target_for_scope(args.scope, args.project_path, manifest)
    if args.dry_run:
        print(f"[DRY RUN] Would install profile '{profile}' to {target} using {mode} mode")
    else:
        target.mkdir(parents=True, exist_ok=True)
        lock_path.parent.mkdir(parents=True, exist_ok=True)

    pack_name = str(manifest.get("name", DEFAULT_PACK_NAME))
    source_repo = git_remote()
    source_commit = git_commit()
    installed_at = utc_now()
    installed: Dict[str, Any] = {}
    skipped: Dict[str, str] = {}

    for name in selected:
        skill = skills[name]
        dst = target / name
        marker = {
            "managed_by": "skillpack",
            "pack_name": pack_name,
            "source_repo": source_repo,
            "source_commit": source_commit,
            "profile": profile,
            "install_mode": mode,
            "skill_name": name,
            "skill_hash": skill.hash,
            "installed_at": installed_at,
        }

        if dst.exists() or dst.is_symlink():
            existing_marker = read_marker(dst)
            if not existing_marker or existing_marker.get("managed_by") != "skillpack":
                skipped[name] = "unmanaged skill exists; preserving local copy"
                if not args.quiet:
                    print(f"SKIP {name}: unmanaged skill exists at {dst}")
                continue
            if not args.dry_run:
                if dst.is_symlink() or dst.is_file():
                    dst.unlink()
                else:
                    shutil.rmtree(dst)

        if args.dry_run:
            print(f"[DRY RUN] Would install {name} -> {dst}")
        else:
            if mode == "copy":
                copy_skill(skill.path, dst)
            else:
                symlink_skill(skill.path, dst)
            try:
                write_marker(dst, marker)
            except Exception as exc:
                # Symlink mode writes to the source directory; if that fails, lock still records ownership.
                if not args.quiet:
                    print(f"WARN {name}: could not write ownership marker: {exc}")
        installed[name] = {
            "source_path": str(skill.path.relative_to(repo_root())),
            "hash": skill.hash,
            "install_mode": mode,
        }
        if not args.quiet:
            print(f"INSTALLED {name} -> {dst}")

    lock = {
        "pack_name": pack_name,
        "display_name": manifest.get("display_name"),
        "pack_version": manifest.get("version"),
        "source_repo": source_repo,
        "source_commit": source_commit,
        "profile": profile,
        "scope": args.scope,
        "target": str(target),
        "install_mode": mode,
        "installed_at": installed_at,
        "skills": installed,
        "skipped_conflicts": skipped,
    }
    if not args.dry_run:
        lock_path.write_text(json.dumps(lock, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    if skipped:
        print(f"Install completed with {len(skipped)} preserved unmanaged conflict(s).")
    else:
        print(f"Install completed: {len(installed)} skill(s) installed to {target}")
    print(f"Lock file: {lock_path}")
    return 0


def read_lock(lock_path: Path) -> Optional[Dict[str, Any]]:
    if not lock_path.exists():
        return None
    try:
        return json.loads(lock_path.read_text(encoding="utf-8"))
    except Exception as exc:
        print(f"WARN: could not read lock file {lock_path}: {exc}")
        return None


def status(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    skills = discover_skills(manifest)
    target, lock_path = target_for_scope(args.scope, args.project_path, manifest)
    lock = read_lock(lock_path)
    pack_name = str(manifest.get("name", DEFAULT_PACK_NAME))

    print(f"Skill Pack: {pack_name} ({manifest.get('version')})")
    print(f"Repo: {git_remote()}")
    print(f"Current commit: {git_commit()}")
    print(f"Scope: {args.scope}")
    print(f"Target: {target}")
    print(f"Lock file: {lock_path}")

    if lock:
        print(f"Installed profile: {lock.get('profile')}")
        print(f"Installed commit: {lock.get('source_commit')}")
        print(f"Installed at: {lock.get('installed_at')}")
    else:
        print("Installed profile: none (no lock file)")

    managed: List[str] = []
    unmanaged: List[str] = []
    missing_locked: List[str] = []
    modified: List[str] = []
    stale: List[str] = []

    if target.exists():
        for child in sorted(target.iterdir()):
            if not (child.is_dir() or child.is_symlink()):
                continue
            marker = read_marker(child)
            if marker and marker.get("managed_by") == "skillpack" and marker.get("pack_name") == pack_name:
                managed.append(child.name)
                if child.name not in skills:
                    stale.append(child.name)
                else:
                    current_hash = hash_skill_dir(child.resolve() if child.is_symlink() else child)
                    locked_hash = None
                    if lock and child.name in (lock.get("skills") or {}):
                        locked_hash = lock["skills"][child.name].get("hash")
                    if locked_hash and current_hash != locked_hash:
                        modified.append(child.name)
            else:
                unmanaged.append(child.name)

    if lock:
        for name in (lock.get("skills") or {}).keys():
            if not (target / name).exists() and not (target / name).is_symlink():
                missing_locked.append(name)

    print("\nManaged skills:")
    if managed:
        for name in managed:
            flags = []
            if name in modified:
                flags.append("modified")
            if name in stale:
                flags.append("stale")
            suffix = f" ({', '.join(flags)})" if flags else ""
            print(f"  - {name}{suffix}")
    else:
        print("  none")

    print("\nUnmanaged/ad-hoc skills:")
    if unmanaged:
        for name in unmanaged:
            print(f"  - {name}")
    else:
        print("  none")

    if missing_locked:
        print("\nMissing locked skills:")
        for name in missing_locked:
            print(f"  - {name}")

    if lock and lock.get("skipped_conflicts"):
        print("\nPreserved conflicts from last install:")
        for name, reason in lock["skipped_conflicts"].items():
            print(f"  - {name}: {reason}")

    return 0


def update(args: argparse.Namespace) -> int:
    if is_git_repo():
        if git_dirty() and not args.allow_dirty:
            raise SkillPackError(
                "working tree has uncommitted changes; commit/stash them or use --allow-dirty"
            )
        if not args.no_pull:
            if git_has_upstream():
                print("Pulling latest changes...")
                proc = run_git(["pull", "--ff-only"])
                if proc.returncode != 0:
                    raise SkillPackError(proc.stderr.strip() or "git pull --ff-only failed")
                if proc.stdout.strip():
                    print(proc.stdout.strip())
            else:
                print("No upstream configured; skipping git pull.")
    else:
        print("Not inside a Git repo; skipping git pull.")

    print("Validating...")
    validation = validate_all(quiet=True)
    if not validation.ok:
        print_validation(validation)
        raise SkillPackError("refusing to update because validation failed")
    print("Validation passed.")

    print("Installing updated managed skills...")
    return install_skills(args)


def package(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    skills = discover_skills(manifest)
    if args.skill:
        selected = [args.skill]
        if args.skill not in skills:
            raise SkillPackError(f"skill not found: {args.skill}")
    else:
        profile = args.profile or manifest.get("default_profile", "all")
        selected = resolve_profile(profile, manifest, skills)

    validation = validate_all(selected=selected, quiet=True)
    if not validation.ok:
        print_validation(validation)
        raise SkillPackError("refusing to package because validation failed")

    out = Path(args.out or "dist/skillpack.zip").expanduser()
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for name in selected:
            skill_dir = skills[name].path
            for path in sorted(skill_dir.rglob("*")):
                if path.is_dir():
                    continue
                rel = path.relative_to(skill_dir.parent).as_posix()
                if rel.endswith(MARKER_NAME) or "__pycache__" in rel:
                    continue
                zf.write(path, rel)
    print(f"Packaged {len(selected)} skill(s) -> {out}")
    return 0


# ---------------------------------------------------------------------------
# CLI commands
# ---------------------------------------------------------------------------


def cmd_list(args: argparse.Namespace) -> int:
    manifest = load_manifest()
    skills = discover_skills(manifest)
    profiles = manifest.get("profiles", {}) or {}

    if args.json:
        data = {
            "pack": {
                "name": manifest.get("name"),
                "display_name": manifest.get("display_name"),
                "version": manifest.get("version"),
            },
            "profiles": list(profiles.keys()),
            "skills": [
                {
                    "name": skill.name,
                    "description": skill.description,
                    "version": skill.metadata.get("skillpack.version"),
                    "tags": skill.metadata.get("skillpack.tags"),
                    "hash": skill.hash,
                }
                for skill in sorted(skills.values(), key=lambda s: s.name)
            ],
        }
        print(json.dumps(data, indent=2, sort_keys=True))
        return 0

    print(f"{manifest.get('display_name', manifest.get('name'))} v{manifest.get('version')}")
    print(f"Default profile: {manifest.get('default_profile')}")
    print("\nProfiles:")
    for name, profile in profiles.items():
        desc = profile.get("description", "") if isinstance(profile, dict) else ""
        try:
            resolved = resolve_profile(name, manifest, skills)
            count = len(resolved)
        except Exception:
            count = 0
        print(f"  - {name}: {desc} ({count} skill(s))")

    print("\nSkills:")
    for skill in sorted(skills.values(), key=lambda s: s.name):
        version = skill.metadata.get("skillpack.version", "")
        tags = skill.metadata.get("skillpack.tags", "")
        meta = []
        if version:
            meta.append(f"v{version}")
        if tags:
            meta.append(str(tags))
        suffix = f" [{'; '.join(meta)}]" if meta else ""
        print(f"  - {skill.name}{suffix}")
        wrapped = textwrap.wrap(skill.description, width=88, subsequent_indent="      ")
        for line in wrapped[:3]:
            print(f"      {line}")
        if len(wrapped) > 3:
            print("      ...")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    selected = None
    if args.profile:
        manifest = load_manifest()
        skills = discover_skills(manifest)
        selected = resolve_profile(args.profile, manifest, skills)
    result = validate_all(selected=selected, quiet=False)
    return 0 if result.ok else 1


def cmd_doctor(args: argparse.Namespace) -> int:
    print("Skill Pack Doctor")
    print(f"Python: {sys.version.split()[0]}")
    print(f"Repo root: {repo_root()}")
    print(f"Manifest: {(repo_root() / 'skillpack.yaml').exists()}")
    print(f"Skills root: {skills_root(load_manifest()).exists()}")
    print(f"Git repo: {is_git_repo()}")
    print(f"Git commit: {git_commit()}")
    print(f"Git remote: {git_remote()}")
    try:
        validation = validate_all(quiet=True)
        print(f"Validation: {'ok' if validation.ok else 'failed'} ({len(validation.errors)} errors, {len(validation.warnings)} warnings)")
    except Exception as exc:
        print(f"Validation: error: {exc}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Manage a Git-backed Skill Pack of Agent Skills.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_list = sub.add_parser("list", help="List available skills and profiles")
    p_list.add_argument("--json", action="store_true", help="Emit JSON")
    p_list.set_defaults(func=cmd_list)

    p_val = sub.add_parser("validate", help="Validate manifest and skills")
    p_val.add_argument("--profile", help="Validate only skills selected by profile")
    p_val.set_defaults(func=cmd_validate)

    p_install = sub.add_parser("install", help="Install skills to Claude Code personal or project scope")
    p_install.add_argument("--scope", choices=["personal", "project"], required=True)
    p_install.add_argument("--project-path", help="Project path for --scope project")
    p_install.add_argument("--profile", default=None, help="Profile to install (default: manifest default)")
    p_install.add_argument("--mode", choices=["copy", "symlink"], default=None, help="Install mode")
    p_install.add_argument("--skip-validation", action="store_true", help="Skip validation before install")
    p_install.add_argument("--dry-run", action="store_true", help="Show actions without writing")
    p_install.add_argument("--quiet", action="store_true", help="Reduce output")
    p_install.set_defaults(func=install_skills)

    p_update = sub.add_parser("update", help="Pull latest repo and sync managed skills")
    p_update.add_argument("--scope", choices=["personal", "project"], required=True)
    p_update.add_argument("--project-path", help="Project path for --scope project")
    p_update.add_argument("--profile", default=None, help="Profile to install (default: manifest default)")
    p_update.add_argument("--mode", choices=["copy", "symlink"], default=None, help="Install mode")
    p_update.add_argument("--skip-validation", action="store_true", help="Skip validation before install")
    p_update.add_argument("--dry-run", action="store_true", help="Show actions without writing")
    p_update.add_argument("--quiet", action="store_true", help="Reduce output")
    p_update.add_argument("--allow-dirty", action="store_true", help="Allow update with dirty working tree")
    p_update.add_argument("--no-pull", action="store_true", help="Skip git pull")
    p_update.set_defaults(func=update)

    p_status = sub.add_parser("status", help="Show installed state")
    p_status.add_argument("--scope", choices=["personal", "project"], required=True)
    p_status.add_argument("--project-path", help="Project path for --scope project")
    p_status.set_defaults(func=status)

    p_pkg = sub.add_parser("package", help="Create zip bundle(s)")
    p_pkg.add_argument("--profile", default=None, help="Profile to package")
    p_pkg.add_argument("--skill", help="Package a single skill")
    p_pkg.add_argument("--out", help="Output zip path")
    p_pkg.set_defaults(func=package)

    p_doc = sub.add_parser("doctor", help="Diagnose common issues")
    p_doc.set_defaults(func=cmd_doctor)

    return parser


def main(argv: Optional[List[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return int(args.func(args) or 0)
    except SkillPackError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    except KeyboardInterrupt:
        print("Interrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
