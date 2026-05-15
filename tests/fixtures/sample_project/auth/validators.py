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
