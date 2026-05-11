---
name: debug-helper
description: >-
  Systematically diagnoses and resolves software bugs through structured debugging.
  Use when the user reports an error, asks to fix a bug, needs help understanding
  a crash, wants to trace through code execution, or needs to identify the root
  cause of unexpected behavior.
metadata:
  skillpack.owner: metaportal-agents
  skillpack.version: "0.1.0"
  skillpack.tags: "coding,debugging,troubleshooting,errors"
  skillpack.source: "metaportal-skillpack"
---

# Debug Helper

## Purpose

Provide a systematic approach to diagnosing and fixing software bugs. Turn "it doesn't work" into "here's the root cause and the fix."

## When to Use

- An error message needs interpretation
- Unexpected behavior needs tracing
- A crash needs root-cause analysis
- Performance needs profiling
- A flaky test needs stabilization
- A regression needs bisecting

## Debugging Process

### 1. Reproduce the Issue
- Get the exact steps to reproduce
- Identify the environment (OS, version, config)
- Determine if it's consistent or intermittent
- Create a minimal reproduction case

### 2. Read the Error
- Full error message including traceback
- Error type and what it means
- Line number and surrounding code
- Stack trace showing the call path

### 3. Form Hypotheses
- What could cause this symptom?
- What changed recently?
- What are the common causes for this error type?
- Rank hypotheses by likelihood

### 4. Test Hypotheses
- Check one hypothesis at a time
- Use logging/print statements strategically
- Inspect variables at each level
- Verify assumptions with evidence

### 5. Fix and Verify
- Make the minimal fix
- Verify the original issue is resolved
- Check for side effects
- Add a test to prevent regression

## Common Error Patterns

### Python

| Error | Common Cause | First Check |
|-------|-------------|-------------|
| `NameError` | Undefined variable | Typo or missing import |
| `TypeError` | Wrong type operation | Type of operands |
| `KeyError` | Missing dict key | Key existence / `.get()` |
| `IndexError` | Out of range index | List length |
| `AttributeError` | Missing attribute | Object type and available attrs |
| `ImportError` | Module not found | Package installed? Correct path? |
| `FileNotFoundError` | Missing file | Absolute vs relative path |
| `RecursionError` | Infinite recursion | Base case logic |

### JavaScript/TypeScript

| Error | Common Cause | First Check |
|-------|-------------|-------------|
| `TypeError: undefined is not a function` | Accessing property on null/undefined | Optional chaining |
| `ReferenceError` | Undeclared variable | Scope and spelling |
| `SyntaxError` | Parse error | Bracket/paren matching |
| `RangeError` | Invalid length/value | Array size or recursion |
| `ENOENT` | File not found | Working directory |

### General

| Symptom | Common Cause |
|---------|-------------|
| Works locally, fails in CI | Environment differences, missing env vars |
| Works once, fails on retry | State not properly cleaned up |
| Slow over time | Memory leak, growing data structure |
| Random failures | Race condition, timing dependency |
| Fails only on large input | Off-by-one, integer overflow, OOM |

## Debugging Tools

### Logging Strategy
```python
# BAD: too vague
print("here")

# GOOD: structured and specific
import logging
logger.debug(f"Processing user_id={user_id}, items={len(items)}, stage=validate")
```

### Binary Search Debugging
When you don't know where the bug is:
1. Place a checkpoint in the middle of the execution
2. Is the state correct at that point?
3. If yes: bug is after the checkpoint
4. If no: bug is before the checkpoint
5. Repeat in the relevant half

### Git Bisect
```bash
git bisect start
git bisect bad HEAD
git bisect good <last-known-good-commit>
# Git checks out middle commit; test it
git bisect good  # or git bisect bad
# Repeat until found
git bisect reset
```

## Output Format

When reporting a debug finding:

```
## Issue
<one-sentence description of the bug>

## Root Cause
<what is actually wrong>

## Evidence
- <traceback, logs, or test output showing the issue>
- <specific line(s) of code involved>

## Fix
<what to change and why>

## Prevention
<how to prevent this class of bug in the future>
```
