import pytest

from . import UnitTest

from rsaw.exceptions import RSAWException, RequestError, ResponseError


class TestRSAWException(UnitTest):
    def test_inheritance(self):
        assert issubclass(RSAWException, Exception)

    def test_catch(self):
        exception = RSAWException("test message")
        with pytest.raises(RSAWException):
            raise exception


class TestRequestError(UnitTest):
    def test_inheritance(self):
        assert issubclass(RequestError, RSAWException)

    def test_catch(self):
        exception = RequestError("test message")
        with pytest.raises(RequestError):
            raise exception


class TestResponseError(UnitTest):
    def test_inheritance(self):
        assert issubclass(ResponseError, RSAWException)

    def test_catch(self):
        exception = ResponseError("test message")
        with pytest.raises(ResponseError):
            raise exception
