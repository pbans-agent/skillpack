# Changelog

All notable changes to this project will be documented here.

## [0.3.0] - 2026-05-09

### Added
- `project-bootstrap` skill — scaffold new projects with proper structure and config
- `debug-helper` skill — systematic debugging and root-cause analysis
- `docs-writer` skill — technical documentation writing (READMEs, API docs, guides)
- `devops` profile — infrastructure, deployment, and project setup skills
- `eval` command — list and describe eval definitions for skills
- `info` command — show detailed info about a specific skill
- `--per-skill` flag on package — create individual zip files per skill
- 13 new tests for Milestone 3 features (27 total)

## [0.2.0] - 2026-05-09

### Added
- `git-workflow` skill — Git branching, committing, and collaboration workflows
- `code-review` skill — Code review for correctness, security, performance, and readability
- `--overwrite-unmanaged` flag on install and update
- `--prune-managed` flag on update to remove stale managed skills
- `--json` flag on status for machine-readable output
- Update diff summary showing added/removed/changed skills between commits
- Upgrade detection in status — shows if upstream has newer commits
- 7 new tests for Milestone 2 features (14 total)

## [0.1.0] - 2026-05-09

### Added
- Initial Skill Pack repository structure
- `skillpack.yaml` manifest with all/coding/research profiles
- `scripts/skillpack.py` CLI with list, validate, install, update, status, package, and doctor commands
- Copy and symlink install modes
- Preserve-unmanaged-skill conflict policy
- Ownership markers and install lock files
- Built-in `skillpack-maintainer` skill
- `example-skill` reference implementation
- Documentation and agent contribution workflow
- Basic unittest suite
- GitHub Actions validation workflow
