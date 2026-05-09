# Skill Pack — New Agent Instructions

Use my Skill Pack to get reusable Agent Skills installed and ready.

## Quick Setup

```bash
# 1. Clone or update the Skill Pack
mkdir -p ~/.skillpacks
if [ -d ~/.skillpacks/metaportal-skillpack/.git ]; then
  git -C ~/.skillpacks/metaportal-skillpack pull --ff-only
else
  git clone https://github.com/pbans-agent/skillpack.git ~/.skillpacks/metaportal-skillpack
fi

# 2. Validate
cd ~/.skillpacks/metaportal-skillpack
python3 scripts/skillpack.py validate

# 3. Install
# For personal scope (available everywhere):
python3 scripts/skillpack.py install --scope personal --profile all

# OR for project scope (current project only):
python3 scripts/skillpack.py install --scope project --project-path . --profile all

# 4. Verify
python3 scripts/skillpack.py status --scope personal
```

## Rules

1. **Do not overwrite** unmanaged/ad-hoc skills that already exist.
2. **Prefer project-scope** install when working inside a repo; otherwise use personal-scope.
3. **Use relevant skills** as you work — they were built to help.
4. **To improve a skill**: create a Git branch, commit changes, run validation, and summarize the proposed update.
5. **Run `python3 scripts/skillpack.py validate`** before committing any skill changes.
6. **Never push directly to main** without explicit user approval — use branches.

## What Gets Installed

Skills are copied into `~/.claude/skills/` (personal) or `<project>/.claude/skills/` (project). Each managed skill gets a `.skillpack-source.json` marker so the system knows it's owned by Skill Pack.

## Updating

```bash
cd ~/.skillpacks/metaportal-skillpack
git pull --ff-only
python3 scripts/skillpack.py update --scope personal --profile all
```

## Contributing

See `docs/contributing-agents.md` in the repo for the full contribution workflow.
