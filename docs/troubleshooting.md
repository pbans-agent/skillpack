# Troubleshooting

## Common Issues

### "skillpack.yaml not found"

Make sure you're running commands from the root of the cloned Skill Pack repo:

```bash
cd ~/.skillpacks/metaportal-skillpack
python3 scripts/skillpack.py validate
```

### "Validation failed: name mismatch"

The `name` field in SKILL.md frontmatter must exactly match the directory name. Check for:
- Extra spaces or hyphens
- Wrong case (names must be lowercase)
- Underscores instead of hyphens

### "Validation failed: description too short"

Descriptions must be at least 20 characters and should include "Use when" guidance with specific trigger contexts. See [skill-authoring-standards.md](skill-authoring-standards.md) for examples.

### "Install failed: unmanaged skill exists"

An existing skill with the same name was found that is not managed by Skill Pack. Options:
1. Remove or rename the unmanaged skill manually, then re-run install
2. Use `--overwrite-unmanaged` flag (not yet available in V1)
3. Skip this skill by using a profile that excludes it

### "Update failed: dirty working tree"

You have uncommitted changes in the Skill Pack repo. Options:
1. Commit or stash your changes: `git stash` then `python3 scripts/skillpack.py update ...` then `git stash pop`
2. Use `--allow-dirty` flag to update anyway (at your own risk)

### "Command not found: python3"

Python 3 is required. Install it via your system package manager:
- Ubuntu/Debian: `sudo apt install python3`
- macOS: `brew install python3`

### "Permission denied" on scripts

Make scripts executable:
```bash
chmod +x skills/*/scripts/*.py
```

### "No skills installed" after install

Check that you used the correct scope:
- `--scope personal` installs to `~/.claude/skills/`
- `--scope project --project-path /path` installs to `/path/.claude/skills/`

Verify with:
```bash
python3 scripts/skillpack.py status --scope personal
```

### Lock file issues

Personal lock file: `~/.skillpacks/installed/metaportal-skillpack.lock.json`
Project lock file: `<project>/.claude/skillpack.lock.json`

If the lock file is corrupted, delete it and re-run install. Skills will be re-installed.

### "Profile not found: <name>"

Check available profiles:
```bash
python3 scripts/skillpack.py list
```

Profiles are defined in `skillpack.yaml` under the `profiles` key. The default is `all`.
