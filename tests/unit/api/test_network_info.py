"""Test prsw.stat.network_info."""

import pytest
from ipaddress import IPv4Network
from typing import Iterable
from unittest.mock import patch

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.network_info import NetworkInfo


class TestNetworkInfo(UnitTest):
    RESPONSE = {
        "messages": [],
        "see_also": [],
        "version": "1.0",
        "data_call_status": "supported",
        "cached": False,
        "data": {"asns": ["37385", "12345"], "prefix": "41.138.32.0/20"},
        "query_id": "20210416152809-c8fafa0e-772a-4b19-8ebb-d1aca80463a0",
        "process_time": 64,
        "server_id": "app123",
        "build_version": "live.2021.4.14.157",
        "status": "ok",
        "status_code": 200,
        "time": "2021-04-16T15:31:09.830045",
    }

    def setup(self):
        url = f"{API_URL}{NetworkInfo.PATH}data.json?resource=41.138.32.10"

        self.api_response = Output(url, **TestNetworkInfo.RESPONSE)
        self.params = {"preferred_version": NetworkInfo.VERSION}

        return super().setup()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called()
            mocked_get.assered_called_with(NetworkInfo.PATH, self.params)

    def test__init__valid_params(self, mock_get):
        response = NetworkInfo(mock_get.ripestat, "41.138.32.10")
        assert isinstance(response, NetworkInfo)

    def test__init__invalid_resource(self):
        with pytest.raises(ValueError):
            NetworkInfo(self.ripestat, resource="invalid")

    def test_asns(self, mock_get):
        response = NetworkInfo(mock_get.ripestat, "41.138.32.10")
        assert isinstance(response.asns, Iterable)

        for asn in TestNetworkInfo.RESPONSE["data"]["asns"]:
            assert int(asn) in response.asns

    def test_prefix(self, mock_get):
        response = NetworkInfo(mock_get.ripestat, "41.138.32.10")
        prefix = TestNetworkInfo.RESPONSE["data"]["prefix"]

        assert isinstance(response.prefix, IPv4Network)
        assert response.prefix == IPv4Network(prefix)
