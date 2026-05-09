# Skill Authoring Standards

## Skill Structure

```
skills/<skill-name>/
├── SKILL.md          # Required — skill definition with frontmatter
├── references/       # Optional — detailed documentation
├── scripts/          # Optional — executable scripts
├── assets/           # Optional — templates, examples, static files
└── evals/            # Optional — evaluation definitions
    ├── evals.json    # Eval definitions
    └── files/        # Input files for evals
```

## SKILL.md

### Required Frontmatter

```yaml
---
name: skill-name
description: >-
  What the skill does and when to use it.
  Include specific trigger words and contexts.
---
```

### Name Rules
- Must match the parent directory name exactly
- Lowercase letters, numbers, and hyphens only
- No spaces, underscores, or special characters
- Examples: `git-commit-helper`, `code-review`, `research-synthesis`

### Description Rules

**Good descriptions** (use as templates):

```yaml
description: >-
  Generates descriptive commit messages by analyzing git diffs.
  Use when the user asks for help writing commit messages,
  reviewing staged changes, summarizing changes, or preparing commits.
```

```yaml
description: >-
  Reviews and improves Agent Skills in a Skill Pack repo.
  Use when the user asks to create, edit, deduplicate, validate,
  test, install, update, version, or maintain reusable AI agent skills.
```

**Bad descriptions** (avoid):

```yaml
description: Helps with commits.
description: A useful skill for agents.
description: Does git stuff.
```

Rules:
- Must say **what** the skill does
- Must say **when** to use it (include "Use when...")
- Include trigger words an agent would match on
- Be specific, not vague
- Minimum 40 characters recommended

### Optional Metadata

```yaml
metadata:
  skillpack.owner: owner-name
  skillpack.version: "0.1.0"
  skillpack.tags: "tag1,tag2,tag3"
  skillpack.source: "metaportal-skillpack"
```

### Content Organization

- Keep SKILL.md concise and focused
- Use clear headings: `# Title`, `## Purpose`, `## When to Use`, `## How It Works`
- Move detailed content into `references/` directory
- Link to references with markdown: `[Reference Name](references/file.md)`
- Include a `## File References` section listing reference files with "when to read" guidance
- Use examples when output quality depends on format

**Example SKILL.md structure:**

```markdown
---
name: my-skill
description: >-
  What it does and when to use it.
---

# My Skill

## Purpose
One-sentence purpose.

## When to Use
- Scenario 1
- Scenario 2

## How It Works
Steps the agent should follow.

## File References
- [Detailed Guide](references/guide.md) — read when you need implementation details
```

## Scripts

Scripts in `scripts/` should follow these conventions:

### Required
- **Non-interactive**: No `input()` prompts. Accept input via flags, env vars, stdin, or file paths.
- **Help text**: Must have `--help` with clear usage documentation.

### Recommended
- **Structured output**: JSON/CSV/TSV where useful (with `--format` flag)
- **Error messages**: Clear, actionable error messages
- **Dry-run**: `--dry-run` flag for risky or stateful operations
- **Bounded output**: Support `--limit`/`--offset` for potentially large output
- **Safe defaults**: Default behavior should be the safest option

### Example

```python
#!/usr/bin/env python3
"""Brief description of what the script does.

Usage:
    python3 myscript.py --input file.txt
    python3 myscript.py --input file.txt --format json
    python3 myscript.py --help
"""

import argparse
import json
import sys

def main():
    parser = argparse.ArgumentParser(description="What this script does.")
    parser.add_argument("--input", required=True, help="Input file path")
    parser.add_argument("--format", choices=["text", "json"], default="text")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be done")
    args = parser.parse_args()

    if args.dry_run:
        print(f"[DRY RUN] Would process: {args.input}")
        return

    # ... actual logic ...

if __name__ == "__main__":
    main()
```

## Evals

Evaluation files help track skill quality over time.

### Structure

```
evals/
├── evals.json       # Eval definitions
└── files/           # Optional input files
    └── input1.txt
```

### evals.json Format

```json
{
  "skill_name": "my-skill",
  "evals": [
    {
      "id": "basic-use-case",
      "prompt": "A realistic prompt testing the skill.",
      "expected_output": "What the expected output should look like.",
      "files": ["files/input1.txt"]
    }
  ]
}
```

### Rules
- Use realistic prompts that match actual use cases
- Describe expected output clearly enough for comparison
- Keep evals independent — each should test one scenario
- An agent should be able to read the eval and run it manually

## Assets

Static files in `assets/`:
- Templates the skill uses
- Example files
- Configuration templates
- Any non-executable resources

## Versioning

Update `skillpack.version` in frontmatter when making meaningful changes:
- **Major**: Skill purpose or interface changes significantly
- **Minor**: New capabilities added
- **Patch**: Bug fixes, description improvements

Use semantic versioning: `"0.1.0"`, `"0.2.0"`, `"1.0.0"`
