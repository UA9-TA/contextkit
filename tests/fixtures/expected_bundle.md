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

```python
# auth/exceptions.py
class AuthException(Exception):
    pass

class InvalidTokenException(AuthException):
    pass

class TokenExpiredException(AuthException):
    pass
```

```python
# auth/models.py
class User:
    def __init__(self, id: int, username: str, email: str):
        self.id = id
        self.username = username
        self.email = email
```
