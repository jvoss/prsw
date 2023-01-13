"""Test prsw.stat.ris_peers."""

import pytest
from datetime import datetime
from ipaddress import IPv4Address
from typing import Iterable
from unittest.mock import patch

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.ris_peers import RISPeers


class TestRISPeers(UnitTest):
    RESPONSE = {
        "messages": [
            [
                "info",
                "Query time has been set to the latest time (2021-04-17 16:00 UTC) data is available for.",
            ]
        ],
        "see_also": [],
        "version": "1.0",
        "data_call_status": "supported",
        "cached": False,
        "data": {
            "peers": {
                "rrc18": [
                    {
                        "asn": "13041",
                        "ip": "193.242.98.38",
                        "v4_prefix_count": 10,
                        "v6_prefix_count": 0,
                    },
                ]
            },
            "latest_time": "2021-04-17T16:00:00",
            "earliest_time": "2001-03-24T00:00:00",
            "parameters": {"query_time": "2021-04-17T16:00:00"},
        },
        "query_id": "20210417171436-e34a045f-482f-43ce-b99e-109c2962f207",
        "process_time": 29,
        "server_id": "app138",
        "build_version": "live.2021.4.14.157",
        "status": "ok",
        "status_code": 200,
        "time": "2021-04-17T17:14:36.207593",
    }

    def setup_method(self):
        url = f"{API_URL}{RISPeers.PATH}data.json?"

        self.api_response = Output(url, **TestRISPeers.RESPONSE)
        self.params = {"preferred_version": RISPeers.VERSION}

        return super().setup_method()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup_method()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called_with(RISPeers.PATH, self.params)

    def test__init__valid_params(self, mock_get):
        response = RISPeers(mock_get.ripestat)
        assert isinstance(response, RISPeers)

    def test__init__valid_query_time(self, mock_get):
        params = self.params.copy()
        params["query_time"] = datetime.fromisoformat("2021-04-17T16:00:00")

        response = RISPeers(mock_get.ripestat, query_time=params["query_time"])

        assert isinstance(response, RISPeers)

        expected_params = params.copy()
        expected_params["query_time"] = "2021-04-17T16:00:00"
        mock_get.params = expected_params

    def test__init__invalid_query_time(self, mock_get):
        params = self.params.copy()
        params["query_time"] = "invalid"

        with pytest.raises(ValueError):
            RISPeers(mock_get.ripestat, params)

    def test__getitem__(self, mock_get):
        response = RISPeers(mock_get.ripestat)
        assert isinstance(response["RRC18"], list)

    def test__iter__(self, mock_get):
        response = RISPeers(mock_get.ripestat)
        assert isinstance(response, Iterable)

        for peer in response:
            assert isinstance(peer, tuple)  # namedtuple Peer

    def test_earliest_time(self, mock_get):
        mock_get.params = self.params  # reset expected params
        response = RISPeers(mock_get.ripestat)
        assert isinstance(response.earliest_time, datetime)

        earliest_time = TestRISPeers.RESPONSE["data"]["earliest_time"]
        assert response.earliest_time == datetime.fromisoformat(earliest_time)

    def test_latest_time(self, mock_get):
        response = RISPeers(mock_get.ripestat)
        assert isinstance(response.latest_time, datetime)

        latest_time = TestRISPeers.RESPONSE["data"]["latest_time"]
        assert response.latest_time == datetime.fromisoformat(latest_time)

    def test_keys(self, mock_get):
        response = RISPeers(mock_get.ripestat)

        assert response.keys().__class__.__name__ == "dict_keys"
        assert list(response.keys()) == [
            k.upper() for k in TestRISPeers.RESPONSE["data"]["peers"].keys()
        ]

    def test_peers(self, mock_get):
        response = RISPeers(mock_get.ripestat)
        assert isinstance(response.peers, dict)

        for rrc, peers in response.peers.items():
            assert isinstance(rrc, str)

            # ensure RRC name is normalized (upcase)
            assert rrc == str(rrc).upper()

            for peer in peers:
                assert isinstance(peer.asn, int)
                assert isinstance(peer.ip, IPv4Address)
                assert isinstance(peer.v4_prefix_count, int)
                assert isinstance(peer.v6_prefix_count, int)

    def test_query_time(self, mock_get):
        response = RISPeers(mock_get.ripestat)
        assert isinstance(response.query_time, datetime)

        query_time = TestRISPeers.RESPONSE["data"]["parameters"]["query_time"]
        assert response.query_time == datetime.fromisoformat(query_time)
