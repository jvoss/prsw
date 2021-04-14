"""RSAW exception classes."""


class RSAWException(Exception):
    """Base Exception that all over exceptions extend."""


class RequestError(RSAWException):
    """Error class for wrapping request errors."""


class ResponseError(RSAWException):
    """Error class for wrapping API response errors."""
