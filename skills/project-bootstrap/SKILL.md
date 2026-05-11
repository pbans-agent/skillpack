---
name: project-bootstrap
description: >-
  Bootstraps new software projects with proper directory structure, configuration files,
  git initialization, and dependency setup. Use when the user asks to create a new project,
  scaffold an application, initialize a repository, or set up a development environment
  for a new codebase.
metadata:
  skillpack.owner: metaportal-agents
  skillpack.version: "0.1.0"
  skillpack.tags: "coding,project,scaffolding,setup"
  skillpack.source: "metaportal-skillpack"
---

# Project Bootstrap

## Purpose

Scaffold new software projects with sensible defaults, proper structure, and modern tooling. Get a project from zero to "first commit" quickly and correctly.

## When to Use

- Creating a new project from scratch
- Scaffolding a new application or service
- Setting up a new repository with proper structure
- Initializing a development environment
- Choosing tech stacks and project templates

## Workflow

1. **Clarify requirements** — What language, framework, and purpose?
2. **Choose template** — Pick the right structure for the project type.
3. **Create directory structure** — Generate files and folders.
4. **Initialize git** — Set up repository with proper `.gitignore`.
5. **Add configuration** — Linting, formatting, testing, CI.
6. **Create initial commit** — Clean starting point.
7. **Verify** — Ensure everything builds/runs.

## Project Types

### Python Package
```
project-name/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── package_name/
│       ├── __init__.py
│       └── ...
├── tests/
│   ├── __init__.py
│   └── test_main.py
└── .github/
    └── workflows/
        └── ci.yml
```

### Python CLI Tool
```
project-name/
├── pyproject.toml
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── cli_name/
│       ├── __init__.py
│       ├── __main__.py
│       └── commands.py
├── tests/
│   └── ...
└── .github/
    └── workflows/
        └── ci.yml
```

### Node.js / TypeScript
```
project-name/
├── package.json
├── tsconfig.json
├── README.md
├── LICENSE
├── .gitignore
├── src/
│   └── index.ts
├── tests/
│   └── ...
└── .github/
    └── workflows/
        └── ci.yml
```

### Chrome Extension
```
extension-name/
├── manifest.json
├── README.md
├── .gitignore
├── src/
│   ├── background.js
│   ├── content.js
│   ├── popup/
│   │   ├── popup.html
│   │   ├── popup.js
│   │   └── popup.css
│   └── options/
├── assets/
│   └── icons/
└── tests/
```

## Configuration Defaults

### Python
- `pyproject.toml` with setuptools or hatchling
- `ruff` for linting and formatting
- `pytest` for testing
- Python 3.10+ minimum

### Node.js
- TypeScript strict mode
- `eslint` + `prettier`
- `vitest` for testing
- Node 20+ target

## Git Setup Rules

- Always initialize with `main` branch
- Add comprehensive `.gitignore` for the language/framework
- Create initial commit with all scaffolded files
- Never commit secrets, `.env` files, or `node_modules`
- Add GitHub Actions CI workflow when appropriate

## Principles

- **Minimal but complete** — include what's needed, nothing extra
- **Modern defaults** — use current best practices for each ecosystem
- **Consistent naming** — lowercase-hyphen for dirs, snake_case for Python
- **Test from the start** — always include a test directory with at least one test
- **Document immediately** — README with setup instructions
