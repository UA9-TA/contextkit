class AuthException(Exception):
    pass

class InvalidTokenException(AuthException):
    pass

class TokenExpiredException(AuthException):
    pass
