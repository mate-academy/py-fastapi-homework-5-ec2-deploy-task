class BaseSecurityError(Exception):
    """Base class for all security-related errors."""

    def __init__(self, message=None) -> None:
        if message is None:
            message = "A security error occurred."
        super().__init__(message)


class TokenExpiredError(BaseSecurityError):
    """Raised when a token has expired."""

    def __init__(self, message="Token has expired.") -> None:
        super().__init__(message)


class InvalidTokenError(BaseSecurityError):
    """Raised when a token is invalid."""

    def __init__(self, message="Invalid token.") -> None:
        super().__init__(message)
