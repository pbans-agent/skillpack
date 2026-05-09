# SkillPack Hermes — Project Context

## What This Is
Building "Skill Pack" — a Git-backed, agent-installable, agent-maintainable source of truth for reusable AI Agent Skills.

## Repo Location
- Local: `~/felix-projects/skillpack-hermes/`
- GitHub: `https://github.com/pbans-agent/skillpack`

## Architecture
- `skillpack.yaml` — pack manifest with profiles
- `skills/` — skill directories (each with SKILL.md + optional references/scripts/assets/evals)
- `scripts/skillpack.py` — Python CLI (list/validate/install/update/status/package/doctor)
- `profiles/` — profile definitions (all/coding/research)
- `docs/` — documentation

## Milestones
1. **Milestone 1** (current): Local MVP — repo skeleton, manifest, CLI with list/validate/install/status, skillpack-maintainer skill, example skill, README, tests
2. **Milestone 2**: Update/version workflow, lock files, conflict handling, GitHub Actions
3. **Milestone 3**: Packaging/export, profiles, evals

## Key Design Decisions
- V1 is "all-in" — install the whole pack by default
- Copy mode is default (not symlink)
- Never overwrite unmanaged/ad-hoc skills
- Git is the versioning/collaboration layer
- Python CLI using only stdlib (argparse, yaml via included parser)
- Ownership marker: `.skillpack-source.json` in each installed skill

## Session Log

### 2026-05-09 — Session 1: Project Bootstrap
- Created full repo skeleton from handoff spec
- Built `scripts/skillpack.py` with list/validate/install/status/update/package/doctor commands
- Created `skillpack.yaml` manifest with all/coding/research profiles
- Created `skillpack-maintainer` skill (built-in self-maintaining skill)
- Created `example-skill` as a reference skill showing proper structure
- Added docs: architecture.md, contributing-agents.md, skill-authoring-standards.md, troubleshooting.md
- Added GitHub Actions validation workflow
- Added basic test suite using temp directories
- README with quickstart, SKILLPACK_AGENT.md with pasteable new-agent instructions
- Ready for GitHub repo creation and first push
