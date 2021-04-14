import pytest
from unittest import mock

from . import UnitTest

from rsaw.api import get, Output, API_URL
from rsaw.exceptions import RequestError, ResponseError


class TestApi(UnitTest):
    RESPONSE = {
        "messages": [],
        "see_also": [],
        "version": "",
        "data_call_status": "",
        "cached": False,
        "query_id": "",
        "process_time": 0,
        "server_id": "",
        "build_version": "",
        "status": "ok",
        "status_code": 200,
        "time": "2021-04-14T14:16:02.142290",
    }

    def mocked_get(*args, **kwargs):
        """Mock requests.get()"""

        class MockResponse:
            def __init__(self, json_data, status_code):
                self.json_data = json_data
                self.status_code = status_code

            def json(self):
                return self.json_data

            def raise_for_status(self):
                pass

        if "/success/" in args[0]:
            return MockResponse(TestApi.RESPONSE, 200)
        if "/notfound/" in args[0]:
            return MockResponse({}, 404)
        if "/error/" in args[0]:
            return MockResponse({}, 500)
        if "/unexpected/" in args[0]:
            return MockResponse({}, 200)


class TestOutput(UnitTest):
    def test__init__valid_params(self):
        output = Output("https://example.com", **TestApi.RESPONSE)
        assert isinstance(output, Output)

    def test__init__invalid_params(self):
        invalid_response = TestApi.RESPONSE.copy()
        invalid_response.__delitem__("status_code")
        with pytest.raises(ResponseError):
            Output("https://example.com", **invalid_response)


class TestGet(UnitTest):
    @mock.patch("requests.get", side_effect=TestApi.mocked_get)
    def test_get__url(self, mock_get):
        response = get("/success/", "param=test")
        mock_get.assert_called()
        assert response._url == API_URL + "/success/data.json?param=test"

    @mock.patch("requests.get", side_effect=TestApi.mocked_get)
    def test_get__successful_response(self, mock_get):
        error_message = f"response is not an instance of {Output}"
        response = get("/success/", "")
        mock_get.assert_called()
        assert isinstance(response, Output), error_message

    @mock.patch("requests.get", side_effect=TestApi.mocked_get)
    def test_get__error_response(self, mock_get):
        with pytest.raises(RequestError):
            get("/error/", "")

        mock_get.assert_called()

    @mock.patch("requests.get", side_effect=TestApi.mocked_get)
    def test_get__not_found_response(self, mock_get):
        with pytest.raises(RequestError):
            get("/notfound/", "")

        mock_get.assert_called()
