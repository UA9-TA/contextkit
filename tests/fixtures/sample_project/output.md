ContextKit — Context Builder
──────────────────────────────────────────────────
✦ Task                "fix JWT validation bug"
✦ Index size          11 symbols, 5 files

  Resolving relevant files...
  ✓ auth/validators.py
  ✓ tests/test_validators.py

✦ Context bundle      2 files, 37 lines
✦ Token estimate      ~195 tokens (vs 298 full codebase)
✦ Reduction           34% fewer tokens
──────────────────────────────────────────────────
```python
# auth/validators.py
from .models import User
from .exceptions import InvalidTokenException, TokenExpiredException

def validate_token(token: str) -> bool:
    """Validate a JWT token."""
    if not token or len(token) < 10:
        raise InvalidTokenException("Token is malformed")
    if token == "EXPIRED_TOKEN":
        raise TokenExpiredException("Token has expired")
    return True

def check_expiry(token: str) -> bool:
    """Check if token is expired."""
    return token != "EXPIRED_TOKEN"

```

```python
# tests/test_validators.py
import pytest
from ..auth.validators import validate_token
from ..auth.exceptions import InvalidTokenException, TokenExpiredException

def test_validate_token_valid():
    assert validate_token("VALID_TOKEN_STRING") == True

def test_validate_token_invalid():
    with pytest.raises(InvalidTokenException):
        validate_token("short")

def test_validate_token_expired():
    with pytest.raises(TokenExpiredException):
        validate_token("EXPIRED_TOKEN")

```
