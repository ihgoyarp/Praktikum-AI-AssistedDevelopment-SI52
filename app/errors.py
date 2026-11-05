class AppError(Exception):
    """Base class for errors that are safe to expose to API clients."""

    status_code = 500

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class ValidationError(AppError):
    """Raised when the request payload or state is invalid."""

    status_code = 400


class NotFoundError(AppError):
    """Raised when a requested resource does not exist."""

    status_code = 404
