"""PRSW exception classes."""


class PRSWException(Exception):
    """Base Exception that all over exceptions extend."""


class RequestError(PRSWException):
    """Error class for wrapping request errors."""


class ResponseError(PRSWException):
    """Error class for wrapping API response errors."""
