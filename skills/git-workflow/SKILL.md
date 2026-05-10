---
name: git-workflow
description: >-
  Manages Git branching, committing, and collaboration workflows for multi-agent and solo projects.
  Use when the user asks to create branches, write commit messages, review staged changes,
  resolve merge conflicts, squash commits, rebase, cherry-pick, or follow conventional commit conventions.
metadata:
  skillpack.owner: metaportal-agents
  skillpack.version: "0.1.0"
  skillpack.tags: "git,coding,workflow,branching,commits"
  skillpack.source: "metaportal-skillpack"
---

# Git Workflow

## Purpose

Provide structured Git workflows for agents working on codebases. Ensure clean history, consistent commit messages, and safe collaboration.

## When to Use

- Creating feature branches or bugfix branches
- Writing descriptive commit messages from diffs
- Reviewing staged or unstaged changes before committing
- Resolving merge or rebase conflicts
- Squashing or reorganizing commits
- Rebasing onto main or another branch
- Cherry-picking specific commits
- Setting up branch naming conventions

## Workflow

### Creating a Branch

```bash
git checkout main
git pull --ff-only
git checkout -b <type>/<short-description>
```

Branch types:
- `feat/` — new feature
- `fix/` — bug fix
- `docs/` — documentation changes
- `refactor/` — code refactoring
- `test/` — adding or updating tests
- `chore/` — maintenance tasks
- `agent/` — agent-initiated changes

### Writing Commit Messages

Use conventional commits:

```
<type>(<scope>): <imperative description>

[optional body with context]
[optional footer with breaking changes or refs]
```

Types: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`, `perf`

Rules:
- Subject line ≤ 72 characters
- Use imperative mood: "add feature" not "added feature"
- Do not end subject with period
- Body explains WHY, not WHAT (diff shows WHAT)
- Reference issues/PRs in footer when applicable

### Before Committing

1. `git status` — see what changed
2. `git diff` — review unstaged changes
3. `git diff --staged` — review staged changes
4. Stage purposefully: `git add -p` for selective staging
5. Write commit message that explains the intent

### Merge Conflict Resolution

1. Inspect the conflict markers in each file
2. Understand what both sides were trying to do
3. Preserve the intent of both changes where possible
4. Never blindly choose "ours" or "theirs"
5. Test after resolving: run validation, tests, linting
6. Stage resolved files: `git add <resolved-files>`
7. Continue: `git rebase --continue` or `git commit`

### Squashing Commits

```bash
git rebase -i HEAD~<n>
# Mark commits to squash, keep the first as "pick"
# Write a clean combined commit message
```

Use squashing when:
- Multiple small commits should be one logical change
- Fixing typos or lint issues immediately after the original commit
- A feature branch has excessive "WIP" commits

### Rebasing

```bash
git checkout <branch>
git fetch origin
git rebase origin/main
```

Rebase instead of merge to keep clean history on feature branches.

## File References

- [Commit Message Templates](references/commit-templates.md) — templates for common commit types
