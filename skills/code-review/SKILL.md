---
name: code-review
description: >-
  Reviews code changes for correctness, security, performance, readability, and maintainability.
  Use when the user asks to review code, check a pull request, inspect a diff, evaluate
  code quality, find bugs in proposed changes, or assess security implications of code modifications.
metadata:
  skillpack.owner: metaportal-agents
  skillpack.version: "0.1.0"
  skillpack.tags: "coding,review,security,quality"
  skillpack.source: "metaportal-skillpack"
---

# Code Review

## Purpose

Systematically review code changes to catch bugs, security issues, performance problems, and maintainability concerns before they reach production.

## When to Use

- Reviewing pull requests or merge requests
- Inspecting staged changes before commit
- Evaluating code quality of generated code
- Checking security implications of changes
- Assessing performance impact of modifications
- Reviewing dependency additions or updates

## Review Checklist

### Correctness
- [ ] Does the code do what it claims to do?
- [ ] Are edge cases handled (null, empty, overflow)?
- [ ] Are error paths handled gracefully?
- [ ] Are there off-by-one errors?
- [ ] Are race conditions possible?

### Security
- [ ] Is user input validated and sanitized?
- [ ] Are there SQL injection, XSS, or command injection risks?
- [ ] Are secrets hardcoded or logged?
- [ ] Are authentication/authorization checks in place?
- [ ] Are file paths constructed safely (path traversal)?

### Performance
- [ ] Are there unnecessary loops or O(n²) operations?
- [ ] Are database queries efficient (N+1 queries)?
- [ ] Are large objects copied unnecessarily?
- [ ] Could this cause memory leaks?
- [ ] Is caching appropriate?

### Readability & Maintainability
- [ ] Is the code self-documenting?
- [ ] Are names clear and consistent?
- [ ] Is the function/method doing one thing?
- [ ] Is the abstraction level appropriate?
- [ ] Are magic numbers replaced with named constants?

### Testing
- [ ] Are there tests for the new behavior?
- [ ] Do tests cover edge cases and error paths?
- [ ] Are tests independent and deterministic?
- [ ] Would existing tests catch regressions?

### Dependencies
- [ ] Are new dependencies justified and minimal?
- [ ] Are dependency versions pinned?
- [ ] Is the dependency well-maintained?
- [ ] Could a stdlib solution work instead?

## Output Format

When reviewing code, structure output as:

```
## Summary
<one-sentence summary of what the code does>

## Issues Found

### Critical
- <issues that must be fixed before merge>

### Warning
- <issues that should be addressed>

### Suggestion
- <improvements that are nice to have>

## Positive Notes
- <things done well>

## Verdict
<APPROVE / REQUEST_CHANGES / COMMENT>
```

## Review Principles

1. **Be specific** — cite exact lines and explain why something is a problem
2. **Explain, don't dictate** — say why, not just what to change
3. **Prioritize** — distinguish critical issues from suggestions
4. **Acknowledge good code** — call out things done well
5. **Stay in scope** — review the change, not the entire codebase
6. **Assume competence** — ask questions before assuming ignorance

## File References

- [Security Patterns](references/security-patterns.md) — common security issues and fixes
- [Performance Patterns](references/performance-patterns.md) — common performance issues and fixes
