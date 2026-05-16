## tests/fixtures/sample_project/auth/validators.py
```py
from auth.models import User
from auth.exceptions import ValidationError

def validate_token(token: str) -> bool:
    """Validate a JWT token."""
    if not token:
        raise ValidationError("Empty token")
    return True

def check_expiry(token: str) -> bool:
    """Check if token is expired."""
    return False
```
## tests/fixtures/sample_project/auth/models.py
```py
class User:
    pass
```
## tests/fixtures/sample_project/auth/exceptions.py
```py
class ValidationError(Exception):
    pass
```
## tests/fixtures/sample_project/tests/test_validators.py
```py
from auth.validators import validate_token

def test_validate_token():
    assert validate_token("abc") == True
```
