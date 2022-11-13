"""Test prsw.stat.routing_history."""

import pytest
import ipaddress
from datetime import datetime
from typing import Iterable
from unittest.mock import patch

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.routing_history import RoutingHistory


class TestRoutingHistory(UnitTest):
    RESPONSE = {
        "messages": [
            [
                "info",
                "Results exclude routes with very low visibility (less than 10 RIS full-feed peers seeing).",
            ]
        ],
        "see_also": [],
        "version": "2.3",
        "data_call_name": "routing-history",
        "data_call_status": "supported - connecting to ursa",
        "cached": False,
        "data": {
            "by_origin": [
                {
                    "origin": "3333",
                    "prefixes": [
                        {
                            "prefix": "193.0.0.0/21",
                            "timelines": [
                                {
                                    "starttime": "2022-11-12T00:00:00",
                                    "endtime": "2022-11-12T07:59:59",
                                    "full_peers_seeing": 369,
                                },
                                {
                                    "starttime": "2022-11-12T08:00:00",
                                    "endtime": "2022-11-12T15:59:59",
                                    "full_peers_seeing": 367,
                                },
                                {
                                    "starttime": "2022-11-12T16:00:00",
                                    "endtime": "2022-11-13T16:00:00",
                                    "full_peers_seeing": 371.67,
                                },
                            ],
                        },
                        {
                            "prefix": "193.0.10.0/23",
                            "timelines": [
                                {
                                    "starttime": "2022-11-12T00:00:00",
                                    "endtime": "2022-11-12T07:59:59",
                                    "full_peers_seeing": 370,
                                },
                                {
                                    "starttime": "2022-11-12T08:00:00",
                                    "endtime": "2022-11-12T15:59:59",
                                    "full_peers_seeing": 368,
                                },
                                {
                                    "starttime": "2022-11-12T16:00:00",
                                    "endtime": "2022-11-13T16:00:00",
                                    "full_peers_seeing": 372.67,
                                },
                            ],
                        },
                        {
                            "prefix": "2001:67c:2e8::/48",
                            "timelines": [
                                {
                                    "starttime": "2022-11-12T00:00:00",
                                    "endtime": "2022-11-12T15:59:59",
                                    "full_peers_seeing": 370.5,
                                },
                                {
                                    "starttime": "2022-11-12T16:00:00",
                                    "endtime": "2022-11-13T16:00:00",
                                    "full_peers_seeing": 374.33,
                                },
                            ],
                        },
                    ],
                }
            ],
            "resource": "3333",
            "query_starttime": "2022-11-12T00:00:00",
            "query_endtime": "2022-11-13T16:00:00",
            "time_granularity": 28800,
            "latest_max_ff_peers": {"v4": 380, "v6": 416},
        },
        "query_id": "20221113214559-1fbcf86f-889b-4685-aabd-0ea3265c84ad",
        "process_time": 23,
        "server_id": "app133",
        "build_version": "live.2022.11.10.129",
        "status": "ok",
        "status_code": 200,
        "time": "2022-11-13T21:45:59.821830",
    }

    def setup(self):
        url = f"{API_URL}{RoutingHistory.PATH}data.json?resource=3333"

        self.api_response = Output(url, **TestRoutingHistory.RESPONSE)
        self.params = {"preferred_version": RoutingHistory.VERSION, "resource": "3333"}

        return super().setup()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called_with(RoutingHistory.PATH, self.params)

    def test__init__valid_resource(self, mock_get):
        response = RoutingHistory(mock_get.ripestat, resource=self.params["resource"])

        assert isinstance(response, RoutingHistory)

    def test__init__valid_starttime(self, mock_get):
        params = self.params.copy()
        params["starttime"] = datetime.fromisoformat("2011-12-12T16:00:00")

        response = RoutingHistory(
            mock_get.ripestat,
            resource=params["resource"],
            starttime=params["starttime"],
        )

        assert isinstance(response, RoutingHistory)

        expected_params = params.copy()
        expected_params["starttime"] = params["starttime"].isoformat()

    def test__init__invalid_starttime(self):
        params = self.params.copy()
        params["starttime"] = "invalid"

        with pytest.raises(ValueError):
            RoutingHistory(
                self.ripestat,
                resource=params["resource"],
                starttime=params["starttime"],
            )

    def test__init__valid_endtime(self, mock_get):
        params = self.params.copy()
        params["endtime"] = datetime.fromisoformat("2021-04-14T16:00:00")

        response = RoutingHistory(
            mock_get.ripestat,
            resource=params["resource"],
            endtime=params["endtime"],
        )

        assert isinstance(response, RoutingHistory)

        expected_params = params.copy()
        expected_params["endtime"] = params["endtime"].isoformat()

    def test__init__invalid_endtime(self):
        params = self.params.copy()
        params["endtime"] = "invalid"

        with pytest.raises(ValueError):
            RoutingHistory(
                self.ripestat,
                resource=params["resource"],
                endtime=params["endtime"],
            )

    def test__init__valid_min_peers(self, mock_get):
        params = self.params.copy()
        params["min_peers"] = 5

        response = RoutingHistory(
            mock_get.ripestat,
            resource=params["resource"],
            min_peers=params["min_peers"],
        )

        expected_params = params.copy()
        expected_params["min_peers"] = "5"
        self.params = expected_params

        assert isinstance(response, RoutingHistory)

    def test__init__invalid_min_peers(self):
        params = self.params.copy()
        params["min_peers"] = "invalid"

        with pytest.raises(ValueError):
            RoutingHistory(
                self.ripestat,
                resource=params["resource"],
                min_peers=params["min_peers"],
            )

    def test__init__invalid_max_rows(self):
        params = self.params.copy()
        params["max_rows"] = "invalid"

        with pytest.raises(ValueError):
            RoutingHistory(
                self.ripestat,
                resource=params["resource"],
                max_rows=params["max_rows"],
            )

    def test__init__valid_max_rows(self):
        params = self.params.copy()
        params["max_rows"] = 10

        try:
            RoutingHistory(
                self.ripestat,
                resource=params["resource"],
                max_rows=params["max_rows"],
            )
        except ValueError:
            pytest.fail("Unexpected ValueError")

    def test__init__invalid_include_first_hop(self):
        params = self.params.copy()
        params["include_first_hop"] = "invalid"

        with pytest.raises(ValueError):
            RoutingHistory(
                self.ripestat,
                resource=params["resource"],
                include_first_hop=params["include_first_hop"],
            )

    def test__init__valid_include_first_hop(self):
        params = self.params.copy()
        params["include_first_hop"] = True

        try:
            RoutingHistory(
                self.ripestat,
                resource=params["resource"],
                include_first_hop=params["include_first_hop"],
            )
        except ValueError:
            pytest.fail("Unexpected ValueError")

    def test__init__invalid_normalize_visibility(self):
        params = self.params.copy()
        params["normalize_visibility"] = "invalid"

        with pytest.raises(ValueError):
            RoutingHistory(
                self.ripestat,
                resource=params["resource"],
                normalize_visibility=params["normalize_visibility"],
            )

    def test__init__valid_normalize_visibility(self):
        params = self.params.copy()
        params["normalize_visibility"] = True

        try:
            RoutingHistory(
                self.ripestat,
                resource=params["resource"],
                normalize_visibility=params["normalize_visibility"],
            )
        except ValueError:
            pytest.fail("Unexpected ValueError")

    def test__getitem__(self, mock_get):
        response = RoutingHistory(mock_get.ripestat, 3333)
        assert isinstance(response[0], tuple)  # namedtuple: AnnouncedPrefix

    def test__iter__(self, mock_get):
        response = RoutingHistory(mock_get.ripestat, 3333)
        assert isinstance(response, Iterable)

    def test__len__(self, mock_get):
        response = RoutingHistory(mock_get.ripestat, 3333)
        assert len(response) == len(TestRoutingHistory.RESPONSE["data"]["by_origin"])

    def test_origin(self, mock_get):
        response = RoutingHistory(mock_get.ripestat, 3333)
        assert isinstance(response.origin, Iterable)

    def test_history(self, mock_get):
        for origin in RoutingHistory(mock_get.ripestat, 3333):
            for prefix_history in origin.prefixes:
                print(prefix_history.prefix)
                assert isinstance(
                    prefix_history.prefix, ipaddress.IPv4Network
                ) or isinstance(prefix_history.prefix, ipaddress.IPv6Network)

            for timeline in prefix_history.timelines:
                assert isinstance(timeline.starttime, datetime)
                assert isinstance(timeline.endtime, datetime)

    def test_latest_max_ff_peers(self, mock_get):
        response = RoutingHistory(mock_get.ripestat, 3333)

        latest_max_ff_peers = TestRoutingHistory.RESPONSE["data"]["latest_max_ff_peers"]
        assert response.latest_max_ff_peers == latest_max_ff_peers

    def test_query_endtime(self, mock_get):
        response = RoutingHistory(mock_get.ripestat, 3333)

        time = TestRoutingHistory.RESPONSE["data"]["query_endtime"]
        assert response.query_endtime == datetime.fromisoformat(time)

    def test_query_starttime(self, mock_get):
        response = RoutingHistory(mock_get.ripestat, 3333)

        time = TestRoutingHistory.RESPONSE["data"]["query_starttime"]
        assert response.query_starttime == datetime.fromisoformat(time)

    def test_resource(self, mock_get):
        response = RoutingHistory(mock_get.ripestat, 3333)

        resource = TestRoutingHistory.RESPONSE["data"]["resource"]
        assert response.resource == int(resource)

    def test_invalid_resource_response(self, mock_get):
        response = RoutingHistory(mock_get.ripestat, 3333)

        response._api.data["resource"] = "invalid"
        assert response.resource == "invalid"
