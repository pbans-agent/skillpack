# Security Policy

## Supported Versions

The current `main` branch is supported for security fixes.

## Reporting a Vulnerability

Open a private security advisory on GitHub or contact the repository owner directly.

## Secret Handling

Skill Pack must never include:

- API keys
- Passwords
- Private tokens
- SSH private keys
- Cookies
- `.env` files
- OAuth credentials

Skills may document required environment variables, but must not contain their values.

## Script Safety

Scripts bundled in skills should:

- Be non-interactive
- Prefer safe defaults
- Support `--dry-run` for destructive or stateful operations
- Avoid broad filesystem/network operations unless clearly documented
