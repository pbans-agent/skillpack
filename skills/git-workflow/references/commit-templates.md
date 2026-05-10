# Commit Message Templates

## Feature

```
feat(<scope>): <imperative description>

<optional context about why this feature was added>

<optional breaking changes>
```

Example:
```
feat(auth): add OAuth2 PKCE flow for mobile clients

Mobile clients cannot securely store client secrets.
PKCE (Proof Key for Code Exchange) provides a secure
authorization flow without requiring client secrets.

Closes #123
```

## Bug Fix

```
fix(<scope>): <imperative description>

<what was wrong and why>
```

Example:
```
fix(api): handle null response from user endpoint

The user profile endpoint returns null for deleted users.
The client was not checking for null before accessing fields,
causing a NullPointerException on profile fetch.
```

## Documentation

```
docs(<scope>): <description>
```

Example:
```
docs(api): update authentication flow documentation
```

## Refactoring

```
refactor(<scope>): <description>

<why the refactor was needed>
```

## Breaking Change

```
feat(<scope>): <description>

BREAKING CHANGE: <what breaks and migration path>
```

## Agent Commit

```
<type>(<scope>): <description>

Agent-initiated change.
<reason for the change>
```
