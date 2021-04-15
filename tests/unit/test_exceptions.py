import pytest

from . import UnitTest

from prsw.exceptions import PRSWException, RequestError, ResponseError


class TestPRSWException(UnitTest):
    def test_inheritance(self):
        assert issubclass(PRSWException, Exception)

    def test_catch(self):
        exception = PRSWException("test message")
        with pytest.raises(PRSWException):
            raise exception


class TestRequestError(UnitTest):
    def test_inheritance(self):
        assert issubclass(RequestError, PRSWException)

    def test_catch(self):
        exception = RequestError("test message")
        with pytest.raises(RequestError):
            raise exception


class TestResponseError(UnitTest):
    def test_inheritance(self):
        assert issubclass(ResponseError, PRSWException)

    def test_catch(self):
        exception = ResponseError("test message")
        with pytest.raises(ResponseError):
            raise exception
