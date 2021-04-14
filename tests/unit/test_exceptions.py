import pytest

from rsaw.exceptions import RSAWException, RequestError, ResponseError


class TestRSAWException:
    def test_inheritance(self):
        assert issubclass(RSAWException, Exception)

    def test_catch(self):
        exception = RSAWException("test message")
        with pytest.raises(RSAWException):
            raise exception


class TestRequestError:
    def test_inheritance(self):
        assert issubclass(RequestError, RSAWException)

    def test_catch(self):
        exception = RequestError("test message")
        with pytest.raises(RequestError):
            raise exception


class TestResponseError:
    def test_inheritance(self):
        assert issubclass(ResponseError, RSAWException)

    def test_catch(self):
        exception = ResponseError("test message")
        with pytest.raises(ResponseError):
            raise exception
