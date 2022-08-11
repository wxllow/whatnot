class Error(Exception):
    """Base class for exceptions in this module."""

    pass


class AuthenticationError(Error):
    pass


class AuthenticationRequired(AuthenticationError):
    pass


class AuthenticationFailed(AuthenticationError):
    pass
