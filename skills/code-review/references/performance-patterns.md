# Performance Patterns

## Common Issues

### N+1 Queries
```python
# BAD — one query per user
for user in users:
    orders = db.query("SELECT * FROM orders WHERE user_id = %s", user.id)

# GOOD — single query with join or batch
orders = db.query("SELECT * FROM orders WHERE user_id IN %s", (tuple(u.id for u in users),))
```

### Unnecessary Copies
```python
# BAD
data = large_list[:]

# GOOD — use the original if mutation isn't needed
data = large_list
```

### String Concatenation in Loops
```python
# BAD
result = ""
for item in items:
    result += str(item)

# GOOD
result = "".join(str(item) for item in items)
```

### Missing Index Usage
```python
# BAD — full collection scan
matches = [x for x in items if x.id == target_id]

# GOOD — use a dict/index
index = {x.id: x for x in items}
match = index.get(target_id)
```

### Synchronous I/O in Hot Paths
```python
# BAD — blocks the event loop
response = requests.get(url)

# GOOD — async I/O
response = await aiohttp_client.get(url)
```

## Review Questions

- What is the expected data size? Will this scale?
- Is there a hot path where O(n²) would hurt?
- Are there database queries inside loops?
- Could caching eliminate repeated work?
- Is lazy loading appropriate for large datasets?
- Are there unnecessary serialization/deserialization cycles?
