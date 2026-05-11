---
name: docs-writer
description: >-
  Writes clear, structured technical documentation including READMEs, API docs,
  architecture guides, inline code comments, and user guides. Use when the user
  asks to write documentation, create a README, document an API, explain code,
  write a tutorial, or improve existing docs.
metadata:
  skillpack.owner: metaportal-agents
  skillpack.version: "0.1.0"
  skillpack.tags: "docs,writing,documentation,communication"
  skillpack.source: "metaportal-skillpack"
---

# Docs Writer

## Purpose

Create high-quality technical documentation that is clear, accurate, well-structured, and genuinely useful to its audience.

## When to Use

- Writing or updating a README
- Documenting APIs and endpoints
- Creating architecture or design docs
- Writing user guides and tutorials
- Improving inline code comments
- Creating changelog entries
- Writing onboarding documentation

## Documentation Types

### README
Every project needs one. Structure:
1. **What it is** — one-sentence description
2. **Why use it** — key benefits
3. **Quick Start** — get running in < 5 minutes
4. **Installation** — all methods
5. **Usage** — common scenarios with examples
6. **Configuration** — all options
7. **Contributing** — how to help
8. **License** — what others can do

### API Documentation
For each endpoint/function:
1. **What it does** — one sentence
2. **Parameters** — name, type, required/default, description
3. **Returns** — type and structure
4. **Throws** — error types and when
5. **Example** — realistic usage
6. **Notes** — edge cases, gotchas

### Architecture Documentation
1. **Overview** — system diagram and data flow
2. **Components** — what each part does
3. **Decisions** — why, not what (what is in code)
4. **Trade-offs** — what was considered and rejected
5. **Growth areas** — where the architecture may need to change

### Tutorial / Guide
1. **Goal** — what the reader will achieve
2. **Prerequisites** — what they need first
3. **Steps** — numbered, testable, one action each
4. **Verification** — how to confirm each step worked
5. **Next steps** — where to go from here

## Writing Principles

### Clarity
- Short sentences. One idea per sentence.
- Active voice: "The function returns..." not "It is returned by..."
- Concrete examples over abstract descriptions
- Define jargon on first use

### Structure
- Lead with the answer, then explain
- Use headers liberally — scannable is readable
- Tables for parameters and options
- Code blocks for examples — always runnable
- Numbered lists for sequences, bullets for options

### Audience Awareness
- Know who is reading and what they already know
- Beginner docs: explain WHY, not just HOW
- Expert docs: be precise and complete
- Internal docs: can assume context
- External docs: must be self-contained

### Code Examples
```python
# BAD: incomplete, won't run
# Just call the function with some data
result = process(data)

# GOOD: complete, runnable, shows real usage
from mylib import process

data = {"users": [{"name": "Alice", "age": 30}]}
result = process(data, format="json", validate=True)
print(result)
# Output: {"processed": 1, "errors": []}
```

Rules for code examples:
- Always runnable (include imports)
- Use realistic data (not "foo", "bar")
- Show expected output
- Keep minimal — one concept per example
- Test your examples actually work

## Anti-Patterns

- **Dead documentation** — docs that describe code that no longer exists
- **Vague documentation** — "configures the system" (what system? how?)
- **Duplicate documentation** — same info in 3 places, all different
- **Over-documentation** — restating what the code clearly shows
- **Documentation debt** — docs that were never updated after a change

## Maintenance

Documentation is code. It should be:
- Version-controlled alongside the code it describes
- Updated in the same commit as code changes
- Reviewed like code
- Tested (do the examples still work?)
