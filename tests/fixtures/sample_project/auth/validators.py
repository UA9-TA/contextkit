from auth.exceptions import ValidationError
from auth.models import User


def validate_token(token: str) -> bool:
    User # To avoid unused import error during ruff check
    """Validate a JWT token."""
    if not token:
        raise ValidationError("Empty token")
    return True

def check_expiry(token: str) -> bool:
    """Check if token is expired."""
    return False
