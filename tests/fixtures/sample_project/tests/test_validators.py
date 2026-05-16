from auth.validators import validate_token


def test_validate_token():
    assert validate_token("abc")
