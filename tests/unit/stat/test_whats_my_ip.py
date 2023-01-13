"""Test prsw.stat.whats_my_ip."""

import pytest
from ipaddress import IPv6Address
from unittest.mock import patch

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.whats_my_ip import WhatsMyIp


class TestWhatsMyIp(UnitTest):
    RESPONSE = {
        "messages": [],
        "see_also": [],
        "version": "0.1",
        "data_call_status": "supported",
        "cached": False,
        "data": {"ip": "f17d:36e:9d3b:4b39:b3c4:44a:b2b1:45e1"},
        "query_id": "20210416018716-1e8763df-ec11-49ca-a0e3-90bf2103a52e",
        "process_time": 0,
        "server_id": "app132",
        "build_version": "live.2021.4.14.157",
        "status": "ok",
        "status_code": 200,
        "time": "2021-04-16T01:39:15.228803",
    }

    def setup_method(self):
        url = f"{API_URL}{WhatsMyIp.PATH}data.json?"

        self.api_response = Output(url, **TestWhatsMyIp.RESPONSE)
        self.params = {"preferred_version": WhatsMyIp.VERSION}

        super().setup_method()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup_method()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called_with(WhatsMyIp.PATH, self.params)

    def test__init__(self, mock_get):
        response = WhatsMyIp(mock_get.ripestat)
        assert isinstance(response, WhatsMyIp)

    def test__str__(self, mock_get):
        response = WhatsMyIp(mock_get.ripestat)
        assert str(response) == TestWhatsMyIp.RESPONSE["data"]["ip"]

    def test_ip(self, mock_get):
        response = WhatsMyIp(mock_get.ripestat)
        assert response.ip == IPv6Address(TestWhatsMyIp.RESPONSE["data"]["ip"])
        assert isinstance(response.ip, IPv6Address)
