---
name: example-skill
description: >-
  A reference example showing proper Skill Pack structure and conventions.
  Use as a template when creating new skills. Demonstrates SKILL.md frontmatter,
  references, scripts, assets, and evals layout.
metadata:
  skillpack.owner: metaportal-agents
  skillpack.version: "0.1.0"
  skillpack.tags: "example,template,reference"
  skillpack.source: "metaportal-skillpack"
---

# Example Skill

## Purpose

This is a reference skill that demonstrates the recommended structure for Skill Pack skills. Copy this directory as a starting point when creating new skills.

## When to Use

- As a template for new skill creation
- As a reference for proper SKILL.md formatting
- To verify that install/validate tooling handles standard skill structures correctly

## Structure

```
example-skill/
├── SKILL.md          # This file — skill definition
├── references/       # Detailed documentation
│   └── usage-guide.md
├── scripts/          # Executable scripts
│   └── hello.py
├── assets/           # Templates and static resources
│   └── template.txt
└── evals/            # Evaluation definitions
    └── evals.json
```

## How It Works

1. The agent reads the description in the frontmatter to decide if this skill is relevant.
2. If relevant, the agent loads the full SKILL.md.
3. If the agent needs more detail, it reads files from `references/`.
4. Scripts in `scripts/` can be executed by the agent when needed.

## Example Script

```bash
python3 skills/example-skill/scripts/hello.py --name "Agent"
```

## File References

- [Usage Guide](references/usage-guide.md) — detailed usage patterns and examples
