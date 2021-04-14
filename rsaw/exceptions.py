"""RSAW exception classes."""


class RequestError(Exception):
    """Error class for wrapping request errors."""

    pass


class ResponseError(Exception):
    """Error class for wrapping API response errors."""

    pass
