---
name: skillpack-maintainer
description: Maintains a Git-backed Skill Pack repository of reusable Agent Skills. Use when the user asks to create, edit, deduplicate, validate, test, install, update, version, package, or improve skills in a central skill repository.
metadata:
  skillpack.owner: metaportal-agents
  skillpack.version: "0.1.0"
  skillpack.tags: "skills,git,maintenance,agent-workflow"
  skillpack.source: "metaportal-skillpack"
---

# Skill Pack Maintainer

## Purpose

Maintain this Skill Pack repo as the source of truth for reusable Agent Skills.

## Location

The Skill Pack repo is at the path where you cloned it (default: `~/.skillpacks/metaportal-skillpack`).

## Core Commands

```bash
python3 scripts/skillpack.py list              # See all skills
python3 scripts/skillpack.py validate          # Validate everything
python3 scripts/skillpack.py install --scope personal --profile all   # Install
python3 scripts/skillpack.py status --scope personal                  # Check state
python3 scripts/skillpack.py update --scope personal --profile all    # Update
```

## Workflow

### When Creating a New Skill

1. Identify what the skill should do and when it should trigger.
2. Create `skills/<skill-name>/` directory (lowercase, hyphens only).
3. Write `SKILL.md` with proper frontmatter (name, description, optional metadata).
4. Keep SKILL.md focused — move detailed content into `references/`.
5. Add scripts to `scripts/` if needed (non-interactive, --help, structured output).
6. Add evals to `evals/` if behavior should be testable.
7. Update `skillpack.yaml` if adding to specific profiles.
8. Run `python3 scripts/skillpack.py validate`.
9. Commit with: `feat(<skill-name>): <description>`.

### When Editing an Existing Skill

1. Pull latest main: `git pull --ff-only`.
2. Create a focused branch: `git checkout -b agent/update-<skill-name>-<purpose>`.
3. Make minimal, focused edits.
4. Run `python3 scripts/skillpack.py validate`.
5. Run skill-specific evals if they exist.
6. Commit with: `fix(<skill-name>): <description>` or `feat(<skill-name>): <description>`.
7. Summarize: what changed, why, validation results, risks.

### When Improving Install/Sync Tooling

1. Pull latest main.
2. Create branch: `git checkout -b agent/tooling-<purpose>`.
3. Edit `scripts/skillpack.py` or related files.
4. Run existing tests: `python3 -m unittest discover -s tests -p 'test_*.py' -v`.
5. Add new tests for new behavior.
6. Commit with: `feat(tooling): <description>`.

## Guardrails

- **Do not** overwrite ad-hoc/unmanaged skills during install.
- **Do not** store credentials or private secrets in skills.
- **Do not** add broad/destructive scripts without dry-run support.
- **Do not** resolve Git conflicts blindly — inspect both versions.
- **Do not** bloat SKILL.md when a referenced file is better.
- **Do not** push directly to main without user approval.

## SKILL.md Frontmatter

Required fields:

```yaml
---
name: skill-name              # Must match directory name
description: >-
  Clear, trigger-rich description. Use when the user asks to...
---
```

Optional metadata:

```yaml
metadata:
  skillpack.owner: metaportal-agents
  skillpack.version: "0.1.0"
  skillpack.tags: "tag1,tag2"
  skillpack.source: "metaportal-skillpack"
```

## Validation Checks

The `validate` command checks:
- `skillpack.yaml` exists and is parseable
- Every skill has `SKILL.md` with valid frontmatter
- Directory name matches frontmatter `name`
- `name` is lowercase with hyphens only
- `description` exists and is not too short or vague
- Referenced files in markdown links exist
- Scripts have help text
- No secret-looking files

## File References

- [Skill Authoring Standards](references/authoring-standards.md) — detailed rules for writing skills
- [Contributing Guide](../../docs/contributing-agents.md) — agent contribution workflow
