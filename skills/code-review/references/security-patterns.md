# Security Patterns

## Common Vulnerabilities

### SQL Injection
```python
# BAD
query = f"SELECT * FROM users WHERE id = {user_id}"

# GOOD
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))
```

### Command Injection
```python
# BAD
os.system(f"convert {filename} output.png")

# GOOD
subprocess.run(["convert", filename, "output.png"], check=True)
```

### Path Traversal
```python
# BAD
path = os.path.join(base_dir, user_filename)

# GOOD
path = os.path.realpath(os.path.join(base_dir, user_filename))
if not path.startswith(os.path.realpath(base_dir)):
    raise ValueError("invalid path")
```

### XSS (Cross-Site Scripting)
```python
# BAD (in HTML template)
return f"<div>{user_input}</div>"

# GOOD
import html
return f"<div>{html.escape(user_input)}</div>"
```

### Hardcoded Secrets
```python
# BAD
API_KEY = "sk-abc123..."

# GOOD
API_KEY = os.environ["API_KEY"]
```

### Insecure Deserialization
```python
# BAD
data = pickle.loads(user_input)

# GOOD
data = json.loads(user_input)
```

## Review Focus Areas

- Authentication and authorization checks
- Input validation at trust boundaries
- Output encoding for the correct context (HTML, JS, URL, SQL)
- Logging that doesn't include sensitive data
- Error messages that don't leak internals
- File operations with proper path validation
- Cryptographic operations using modern algorithms
- Rate limiting on public endpoints
