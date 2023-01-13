"""Test prsw.api.looking_glass."""

import pytest
from datetime import datetime
from typing import Iterable
from unittest.mock import patch

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.looking_glass import LookingGlass


class TestLookingGlass(UnitTest):
    RESPONSE = {
        "messages": [],
        "see_also": [],
        "version": "2.1",
        "data_call_status": "supported",
        "cached": False,
        "data": {
            "rrcs": [
                {
                    "rrc": "RRC00",
                    "location": "Amsterdam, Netherlands",
                    "peers": [
                        {
                            "asn_origin": "1205",
                            "as_path": "34854 6939 1853 1853 1205",
                            "community": "34854:1009",
                            "last_updated": "2021-04-15T08:21:07",
                            "prefix": "140.78.0.0/16",
                            "peer": "2.56.11.1",
                            "origin": "IGP",
                            "next_hop": "2.56.11.1",
                            "latest_time": "2021-04-15T12:51:19",
                        },
                    ],
                },
            ],
            "query_time": "2021-04-15T12:51:22",
            "latest_time": "2021-04-15T12:51:04",
            "parameters": {"resource": "140.78.0.0/16"},
        },
        "query_id": "20210415125122-96ed15ff-31d8-41b9-b1d0-d0c3f293f0c1",
        "process_time": 79,
        "server_id": "app114",
        "build_version": "live.2021.4.14.157",
        "status": "ok",
        "status_code": 200,
        "time": "2021-04-15T12:45:22.211516",
    }

    def setup_method(self):
        url = f"{API_URL}{LookingGlass.PATH}data.json?resource=140.78.0.0/16"

        self.api_response = Output(url, **TestLookingGlass.RESPONSE)
        self.params = {
            "preferred_version": LookingGlass.VERSION,
            "resource": "140.78.0.0/16",
        }

        return super().setup_method()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup_method()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called_with(LookingGlass.PATH, self.params)

    def test__init__valid_resource(self, mock_get):
        response = LookingGlass(mock_get.ripestat, resource=self.params["resource"])
        assert isinstance(response, LookingGlass)

    def test__init__invalid_resource(self):
        with pytest.raises(ValueError):
            LookingGlass(self.ripestat, resource="invalid-prefix")

    def test__getitem__(self, mock_get):
        response = LookingGlass(mock_get.ripestat, resource=self.params["resource"])
        assert isinstance(response["RRC00"], tuple)  # namedtuple: RRC by RRC key

    def test__iter__(self, mock_get):
        response = LookingGlass(mock_get.ripestat, resource=self.params["resource"])
        assert isinstance(response, Iterable)

    def test__len__(self, mock_get):
        response = LookingGlass(mock_get.ripestat, resource=self.params["resource"])
        assert len(response) == len(TestLookingGlass.RESPONSE["data"]["rrcs"])

    def test_objectify_rrcs(self, mock_get):
        response = LookingGlass(mock_get.ripestat, resource=self.params["resource"])

        for collector in response:
            assert isinstance(collector, tuple)  # namedtuple: RRC
            assert "rrc" in collector.__dir__()
            assert "location" in collector.__dir__()
            assert "peers" in collector.__dir__()

            for peer in collector.peers:
                assert isinstance(peer, tuple)  # namedtuple: Peer
                assert "asn_origin" in peer.__dir__()
                assert "as_path" in peer.__dir__()
                assert "community" in peer.__dir__()
                assert "last_updated" in peer.__dir__()
                assert "prefix" in peer.__dir__()
                assert "peer" in peer.__dir__()
                assert "origin" in peer.__dir__()
                assert "next_hop" in peer.__dir__()
                assert "latest_time" in peer.__dir__()

    def test_latest_time(self, mock_get):
        response = LookingGlass(mock_get.ripestat, resource=self.params["resource"])

        latest_time = TestLookingGlass.RESPONSE["data"]["latest_time"]
        assert response.latest_time == datetime.fromisoformat(latest_time)

    def test_query_time(self, mock_get):
        response = LookingGlass(mock_get.ripestat, resource=self.params["resource"])

        time = TestLookingGlass.RESPONSE["data"]["query_time"]
        assert response.query_time == datetime.fromisoformat(time)

    def test_peers(self, mock_get):
        response = LookingGlass(mock_get.ripestat, resource=self.params["resource"])

        assert isinstance(response.peers, list)

        for peer in response.peers:
            assert isinstance(peer, tuple)  # namedtuple: Peer

    def test_rrcs(self, mock_get):
        response = LookingGlass(mock_get.ripestat, resource=self.params["resource"])

        assert isinstance(response.rrcs, dict)

        for name, route_server in response.rrcs.items():
            assert isinstance(name, str)  # RRC name: 'RRC00'
            assert isinstance(route_server, tuple)  # namedtuple: RRC
