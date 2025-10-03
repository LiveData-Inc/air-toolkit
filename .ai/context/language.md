# Python Code Conventions

**Last Updated**: YYYY-MM-DD
**AI Assistants**: Follow these Python-specific conventions

## Critical Rules

1. **Type Hints**: Required for all public APIs

   ```python
   def process_data(items: list[dict], limit: int = 100) -> dict[str, Any]:
       """Docstring required for public functions."""
   ```

2. **Path Handling**: Use `pathlib.Path`, never string concatenation

   ```python
   # ✅ Good
   from pathlib import Path
   config_path = Path("config") / "settings.json"

   # ❌ Bad
   config_path = "config/" + "settings.json"
   ```

3. **Dependency Management**: Use `pyproject.toml`

   ```toml
   [project]
   dependencies = ["requests>=2.31.0"]
   ```

4. **Error Handling**: Custom exceptions inherit from base

   ```python
   class AppError(Exception):
       """Base for all application errors."""

   class ValidationError(AppError):
       """Invalid input data."""
   ```

## Naming Conventions

- **Files/Modules**: `snake_case.py`
- **Functions/Variables**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private**: `_leading_underscore`

## Common Mistakes to Avoid

```python
# ❌ Mutable default arguments
def append_to(item, items=[]):
    items.append(item)
    return items

# ✅ Use None and initialize
def append_to(item, items=None):
    items = items if items is not None else []
    items.append(item)
    return items

# ❌ Catching generic Exception
try:
    risky_operation()
except Exception:
    pass

# ✅ Catch specific exceptions
try:
    risky_operation()
except (ValueError, KeyError) as e:
    logger.error(f"Operation failed: {e}")
    raise

# ❌ String formatting without f-strings
message = "User {} has {} items".format(user, count)

# ✅ Use f-strings (Python 3.6+)
message = f"User {user} has {count} items"
```

## Async/Await

```python
# Use async/await for I/O operations
async def fetch_data(url: str) -> dict:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            return await response.json()

# Run concurrent operations with gather
results = await asyncio.gather(
    fetch_data(url1),
    fetch_data(url2),
    fetch_data(url3)
)
```

## Standard Tools

- **Formatter**: `black` (line length: 100)
- **Import Sorter**: `isort --profile black`
- **Linter**: `ruff` (replaces flake8, pylint, isort)
- **Type Checker**: `mypy --strict`

```toml
# pyproject.toml
[tool.black]
line-length = 100

[tool.ruff]
line-length = 100
select = ["E", "F", "I", "N", "W"]

[tool.mypy]
strict = true
warn_return_any = true
warn_unused_configs = true
```

## Testing

```python
# Use pytest, organize with AAA pattern
def test_user_creation():
    # Arrange
    user_data = {"name": "John", "email": "john@example.com"}

    # Act
    user = create_user(user_data)

    # Assert
    assert user.name == "John"
    assert user.email == "john@example.com"

# Use fixtures for common setup
@pytest.fixture
def db_session():
    session = create_test_session()
    yield session
    session.close()
```

## Documentation

```python
def complex_function(param: str, limit: int = 10) -> list[dict]:
    """Brief one-line description.

    Longer description if needed. Explain why, not what.

    Args:
        param: Description of param
        limit: Maximum number of results (default: 10)

    Returns:
        List of result dictionaries

    Raises:
        ValueError: When param is invalid
    """
```

## Virtual Environments

```bash
# Use venv or uv (faster alternative)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Or use uv (recommended)
pip install uv
uv venv
uv pip install -r requirements.txt
```

## Project-Specific Conventions

<!-- Add your project-specific Python rules below -->

### [Custom Rule 1]

[Description]

### [Custom Rule 2]

[Description]

---

**Remember**: These conventions exist to maintain code quality. When you need to deviate, document it in a task file with rationale.
