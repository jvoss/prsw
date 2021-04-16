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

    @pytest.fixture(autouse=True)
    def setup(self):
        url = f"{API_URL}{WhatsMyIp}data.json?"

        self.api_response = Output(url, **TestWhatsMyIp.RESPONSE)
        self.params = {"preferred_version": WhatsMyIp.VERSION}

        super().setup()

        with patch.object(self.ripestat, "_get") as mock_get:
            mock_get.return_value = self.api_response

            yield self

            mock_get.assert_called()
            mock_get.assert_called_with(WhatsMyIp.PATH, self.params)

    def test__init__(self):
        response = WhatsMyIp(self.ripestat)
        assert isinstance(response, WhatsMyIp)

    def test__str__(self):
        response = WhatsMyIp(self.ripestat)
        assert str(response) == TestWhatsMyIp.RESPONSE["data"]["ip"]

    def test_ip(self):
        response = WhatsMyIp(self.ripestat)
        assert response.ip == IPv6Address(TestWhatsMyIp.RESPONSE["data"]["ip"])
        assert isinstance(response.ip, IPv6Address)
