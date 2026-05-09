# Contributing Guide for Agents

## Workflow

### 1. Start Clean

```bash
git checkout main
git pull --ff-only
```

### 2. Create a Branch

```bash
git checkout -b agent/<action>-<skill-name>-<short-purpose>
```

Examples:
- `agent/add-git-commit-helper`
- `agent/update-example-skill-tighten-description`
- `agent/fix-tooling-preserve-unmanaged`

### 3. Make Focused Edits

- Keep edits focused on one skill or one concern per commit
- Do not edit multiple unrelated skills in one commit
- Move detailed content into `references/` instead of bloating SKILL.md
- Add evals for behavior changes

### 4. Validate

```bash
python3 scripts/skillpack.py validate
```

Fix any issues before committing.

### 5. Test

```bash
python3 -m unittest discover -s tests -p 'test_*.py' -v
```

Add new tests for new behavior.

### 6. Commit

Use conventional commit style:

```
feat(<skill-name>): add new capability
fix(<skill-name>): fix specific issue
docs: update documentation
chore: update tooling
```

### 7. Summarize

After committing, report:
- **What changed** — files and skills touched
- **Why it changed** — the reasoning
- **Validation results** — pass/fail with any warnings
- **Test results** — pass/fail
- **Unresolved risks** — anything uncertain
- **Suggested next step** — merge, PR, more testing, etc.

## Conflict Handling

When two agents update the same skill:

1. `git pull --rebase origin main` or `git merge main`
2. If conflicts occur, **inspect both versions**
3. Preserve user-specific workflow intent from both sides
4. **Never** resolve conflicts by blindly choosing ours/theirs
5. Run validation after resolving
6. If unsure, ask the user

## What NOT to Do

- **Do not** push directly to main without user approval
- **Do not** store credentials or secrets in skills
- **Do not** add broad/destructive scripts without `--dry-run`
- **Do not** bloat SKILL.md — use references/
- **Do not** overwrite unmanaged/ad-hoc skills during install
- **Do not** resolve conflicts blindly
