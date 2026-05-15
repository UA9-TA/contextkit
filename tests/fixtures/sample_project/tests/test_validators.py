import pytest

from ..auth.exceptions import InvalidTokenException, TokenExpiredException
from ..auth.validators import validate_token


def test_validate_token_valid():
    assert validate_token("VALID_TOKEN_STRING")

def test_validate_token_invalid():
    with pytest.raises(InvalidTokenException):
        validate_token("short")

def test_validate_token_expired():
    with pytest.raises(TokenExpiredException):
        validate_token("EXPIRED_TOKEN")
