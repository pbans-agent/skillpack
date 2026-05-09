# Example Skill — Usage Guide

## Overview

This guide demonstrates how a skill's reference documentation should be structured.

## Usage Patterns

### Pattern 1: Direct Invocation

When a user asks directly to use this skill:

```
"Use the example skill"
"Run the example"
```

The agent should:
1. Load this SKILL.md
2. Determine what action to take
3. Execute any necessary scripts
4. Return results

### Pattern 2: Implicit Trigger

When a user's request matches the skill description but doesn't name the skill:

```
"Show me a skill template"
"How should I structure a new skill?"
```

The agent should recognize this matches the skill's description triggers.

## Output Format

When this skill is used, output should be:
- Clear and concise
- Include the structure template
- Note any variations for specific use cases

## Tips

- References should be one level deep from SKILL.md
- Include "when to read this" guidance
- Use examples when output style matters
