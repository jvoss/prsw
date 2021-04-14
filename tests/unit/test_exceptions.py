import pytest

from rsaw.exceptions import RSAWException, RequestError, ResponseError


class TestRSAWException:
    def test_inheritance(self):
        assert issubclass(RSAWException, Exception)


class TestRequestError:
    def test_inheritance(self):
        assert issubclass(RequestError, RSAWException)


class TestResponseError:
    def test_inheritance(self):
        assert issubclass(ResponseError, RSAWException)
