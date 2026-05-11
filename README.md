# Skill Pack

A Git-backed, agent-installable, agent-maintainable source of truth for reusable AI Agent Skills.

## Quick Start

### For Agents

```bash
# 1. Clone the repo
mkdir -p ~/.skillpacks
git clone https://github.com/pbans-agent/skillpack.git ~/.skillpacks/metaportal-skillpack

# 2. Validate
cd ~/.skillpacks/metaportal-skillpack
python3 scripts/skillpack.py validate

# 3. Install (personal scope)
python3 scripts/skillpack.py install --scope personal --profile all

# 4. Check status
python3 scripts/skillpack.py status --scope personal
```

### For Humans

1. Clone this repo
2. Run `python3 scripts/skillpack.py list` to see available skills
3. Run `python3 scripts/skillpack.py install --scope personal --profile all` to install everything
4. Or install to a specific project: `python3 scripts/skillpack.py install --scope project --project-path /path/to/project --profile all`

## Commands

| Command | Description |
|---------|-------------|
| `list` | List available skills with descriptions, tags, and profiles |
| `validate` | Validate the manifest and all skills |
| `install` | Install skills to Claude Code personal or project scope |
| `update` | Update managed skills from the repo |
| `status` | Show installed skills, source commit, and conflicts |
| `package` | Create zip bundles for upload |
| `eval` | List and describe eval definitions for skills |
| `info` | Show detailed info about a specific skill |
| `doctor` | Diagnose common issues |

## Testing

```bash
python3 scripts/skillpack.py validate
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

## Install Scopes

- **Personal**: Installs to `~/.claude/skills/` — available in all Claude Code sessions
- **Project**: Installs to `<project>/.claude/skills/` — available only in that project

## Install Modes

- **copy** (default): Copies skill directories. Safe and predictable.
- **symlink**: Creates symlinks back to the cloned repo. Good for development.

## Profiles

| Profile | Description |
|---------|-------------|
| `all` | Every managed skill |
| `coding` | Coding and repo-management skills |
| `research` | Research, planning, and document skills |
| `devops` | Infrastructure, deployment, and project setup |

## Included Skills

| Skill | Description |
|-------|-------------|
| `skillpack-maintainer` | Maintains the Skill Pack repo itself |
| `git-workflow` | Git branching, committing, and collaboration workflows |
| `code-review` | Code review for correctness, security, performance |
| `project-bootstrap` | Scaffold new projects with proper structure |
| `debug-helper` | Systematic debugging and root-cause analysis |
| `docs-writer` | Technical documentation writing |
| `example-skill` | Reference example showing proper structure |

## Safety

- **Never** overwrites unmanaged/ad-hoc skills
- Tracks managed skills via `.skillpack-source.json` ownership markers
- Records installs in lock files for update tracking
- Validates before install when `require_validation` is true

## Contributing

See [docs/contributing-agents.md](docs/contributing-agents.md) for the agent contribution workflow.

## Structure

```
skillpack/
├── README.md                  # This file
├── SKILLPACK_AGENT.md         # Pasteable instructions for new agents
├── skillpack.yaml             # Pack manifest
├── skills/                    # All skill directories
│   ├── skillpack-maintainer/  # Built-in: maintains this repo
│   ├── example-skill/         # Reference example
│   └── ...
├── profiles/                  # Profile definitions
├── scripts/
│   └── skillpack.py           # The CLI
├── docs/                      # Documentation
├── tests/                     # Test suite
└── .github/workflows/         # CI validation
```

## License

MIT
