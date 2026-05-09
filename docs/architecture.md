# Architecture

## Overview

Skill Pack is a Git-backed system for managing reusable AI Agent Skills. It consists of:

1. **A repository** containing skills, a manifest, profiles, and tooling
2. **A Python CLI** for listing, validating, installing, updating, and packaging skills
3. **Install targets** — Claude Code personal (`~/.claude/skills`) and project (`.claude/skills`) scopes

## Design Principles

- **Git is the collaboration layer** — no parallel versioning system
- **File-based skills** — SKILL.md + optional references/scripts/assets/evals
- **Copy by default** — predictable, safe, no accidental repo edits
- **Preserve unmanaged skills** — never overwrite ad-hoc skills
- **Agent-maintainable** — the `skillpack-maintainer` skill teaches agents to maintain the repo

## Data Flow

```
skillpack.yaml (manifest)
    ↓
skills/ (source of truth)
    ↓
scripts/skillpack.py (CLI)
    ↓
~/.claude/skills/ or .claude/skills/ (installed)
    ↓
.claude/skillpack.lock.json (install record)
```

## Key Files

| File | Purpose |
|------|---------|
| `skillpack.yaml` | Pack manifest — name, version, profiles, defaults |
| `skills/*/SKILL.md` | Skill definitions with YAML frontmatter |
| `scripts/skillpack.py` | The CLI tool |
| `profiles/*.yaml` | Profile definitions for subset installs |
| `SKILLPACK_AGENT.md` | Pasteable new-agent instructions |
| `docs/` | Documentation |

## Install Modes

### Copy Mode (default)
- Copies skill directories into target
- Safe and predictable
- Requires `update` command to refresh
- Each installed skill gets `.skillpack-source.json` ownership marker

### Symlink Mode
- Creates symlinks from target back to cloned repo
- Edits in repo are immediately reflected
- Good for development workflows
- Risk: agents may accidentally edit central source

## Ownership Tracking

Each installed skill gets a `.skillpack-source.json`:

```json
{
  "managed_by": "skillpack",
  "pack_name": "metaportal-skillpack",
  "source_repo": "https://github.com/pbans-agent/skillpack",
  "source_commit": "abc123...",
  "profile": "all",
  "installed_at": "2026-05-09T00:00:00Z"
}
```

## Lock Files

### Personal scope
`~/.skillpacks/installed/metaportal-skillpack.lock.json`

### Project scope
`<project>/.claude/skillpack.lock.json`

Lock files record the source repo, commit, profile, and hashes of installed skills.

## Conflict Policy

| Scenario | Behavior |
|----------|----------|
| Target empty | Install normally |
| Target has managed skill | Update (overwrite) |
| Target has unmanaged same-name skill | **Preserve** — do not overwrite, warn user |
| Skill removed from pack | Do not delete installed copy; mark stale in status |

## Validation

The `validate` command checks:
- Manifest parseable and complete
- Every skill has SKILL.md
- Frontmatter has required fields (name, description)
- Directory name matches frontmatter name
- Name follows naming conventions (lowercase, hyphens)
- Description is not too short or vague
- Markdown file references exist
- Scripts have help documentation
- No secret-looking files

## Profiles

Profiles define skill subsets via glob patterns:
- `all` — everything (default)
- `coding` — code and git skills
- `research` — research and planning skills

Profiles are defined in both `skillpack.yaml` and `profiles/*.yaml`.
