# Skill Authoring Standards

## Skill Structure

```
skills/<skill-name>/
├── SKILL.md          # Required — skill definition
├── references/       # Optional — detailed docs
├── scripts/          # Optional — executable scripts
├── assets/           # Optional — templates, examples
└── evals/            # Optional — evaluation definitions
```

## SKILL.md Rules

### Frontmatter (Required)

```yaml
---
name: skill-name
description: >-
  What the skill does and when to use it.
  Include specific trigger words and contexts.
---
```

### Name Constraints
- Must match the directory name exactly
- Lowercase letters, numbers, and hyphens only
- No spaces, underscores, or special characters
- Examples: `git-commit-helper`, `code-review`, `research-synthesis`

### Description Rules
- **Good**: "Generates descriptive commit messages by analyzing git diffs. Use when the user asks for help writing commit messages, reviewing staged changes, or summarizing changes."
- **Bad**: "Helps with commits."
- Must say what the skill does AND when to use it
- Include trigger words an agent would match on
- Avoid vague language

### Content Rules
- Keep SKILL.md concise and focused
- Move detailed content into `references/`
- Use `## File References` section to link to reference files
- Include "when to read this" guidance for references
- Use examples when output quality depends on style or format

## Scripts

Scripts inside `scripts/` should:
- Be non-interactive (no `input()` prompts)
- Accept flags, env vars, stdin, or file paths as input
- Have `--help` documentation
- Emit structured output (JSON/CSV/TSV) where useful
- Use clear error messages
- Support `--dry-run` for risky operations
- Keep output bounded or support `--limit`/`--offset`

## Evals

Eval files in `evals/` should:
- Be JSON format: `evals.json`
- Define realistic prompts and expected outputs
- Include input files in `evals/files/` when needed
- Be runnable by an agent reading the eval definition

## Versioning

Use frontmatter metadata:
```yaml
metadata:
  skillpack.version: "0.1.0"
```

Update version when making meaningful changes to skill behavior.
