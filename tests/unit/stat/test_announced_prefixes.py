"""Test prsw.stat.announced_prefixes."""

import pytest
import ipaddress
from datetime import datetime
from typing import Iterable
from unittest.mock import patch

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.announced_prefixes import AnnouncedPrefixes


class TestAnnouncedPrefixes(UnitTest):
    RESPONSE = {
        "messages": [],
        "see_also": [],
        "version": "1.2",
        "data_call_status": "supported - connecting to ursa",
        "cached": False,
        "query_id": "20210415024133-07420057-7e5a-41b7-bed7-98bc59aeac84",
        "process_time": 5265,
        "server_id": "app149",
        "build_version": "live.2021.4.14.157",
        "status": "ok",
        "status_code": 200,
        "time": "2021-04-14T14:16:03.162290",
        "data": {
            "prefixes": [
                {
                    "prefix": "193.0.10.0/23",
                    "timelines": [
                        {
                            "starttime": "2011-12-12T16:00:00",
                            "endtime": "2011-12-31T16:00:00",
                        },
                        {
                            "starttime": "2012-02-01T00:00:00",
                            "endtime": "2014-01-31T16:00:00",
                        },
                        {
                            "starttime": "2014-03-01T00:00:00",
                            "endtime": "2014-06-04T16:00:00",
                        },
                        {
                            "starttime": "2014-06-06T00:00:00",
                            "endtime": "2015-09-04T08:00:00",
                        },
                        {
                            "starttime": "2015-09-05T00:00:00",
                            "endtime": "2015-12-16T00:00:00",
                        },
                        {
                            "starttime": "2015-12-17T00:00:00",
                            "endtime": "2021-04-14T16:00:00",
                        },
                    ],
                },
            ],
            "query_starttime": "2011-12-12T12:00:00",
            "query_endtime": "2021-04-14T16:00:00",
            "resource": "3333",
            "latest_time": "2021-04-14T16:00:00",
            "earliest_time": "2000-08-01T00:00:00",
        },
    }

    def setup_method(self):
        url = f"{API_URL}{AnnouncedPrefixes.PATH}data.json?resource=3333"

        self.api_response = Output(url, **TestAnnouncedPrefixes.RESPONSE)
        self.params = {
            "preferred_version": AnnouncedPrefixes.VERSION,
            "resource": "3333",
        }

        return super().setup_method()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup_method()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called_with(AnnouncedPrefixes.PATH, self.params)

    def test__init__valid_resource(self, mock_get):
        response = AnnouncedPrefixes(
            mock_get.ripestat, resource=self.params["resource"]
        )

        assert isinstance(response, AnnouncedPrefixes)

    def test__init__valid_starttime(self, mock_get):
        params = self.params.copy()
        params["starttime"] = datetime.fromisoformat("2011-12-12T16:00:00")

        response = AnnouncedPrefixes(
            mock_get.ripestat,
            resource=params["resource"],
            starttime=params["starttime"],
        )

        assert isinstance(response, AnnouncedPrefixes)

        expected_params = params.copy()
        expected_params["starttime"] = params["starttime"].isoformat()

    def test__init__invalid_starttime(self):
        params = self.params.copy()
        params["starttime"] = "invalid"

        with pytest.raises(ValueError):
            AnnouncedPrefixes(
                self.ripestat,
                resource=params["resource"],
                starttime=params["starttime"],
            )

    def test__init__valid_endtime(self, mock_get):
        params = self.params.copy()
        params["endtime"] = datetime.fromisoformat("2021-04-14T16:00:00")

        response = AnnouncedPrefixes(
            mock_get.ripestat,
            resource=params["resource"],
            endtime=params["endtime"],
        )

        assert isinstance(response, AnnouncedPrefixes)

        expected_params = params.copy()
        expected_params["endtime"] = params["endtime"].isoformat()

    def test__init__invalid_endtime(self):
        params = self.params.copy()
        params["endtime"] = "invalid"

        with pytest.raises(ValueError):
            AnnouncedPrefixes(
                self.ripestat,
                resource=params["resource"],
                endtime=params["endtime"],
            )

    def test__init__valid_min_peers_seeing(self, mock_get):
        params = self.params.copy()
        params["min_peers_seeing"] = 5

        response = AnnouncedPrefixes(
            mock_get.ripestat,
            resource=params["resource"],
            min_peers_seeing=params["min_peers_seeing"],
        )

        expected_params = params.copy()
        expected_params["min_peers_seeing"] = "5"

        assert isinstance(response, AnnouncedPrefixes)

    def test__init__invalid_min_peers_seeing(self):
        params = self.params.copy()
        params["min_peers_seeing"] = "invalid"

        with pytest.raises(ValueError):
            AnnouncedPrefixes(
                self.ripestat,
                resource=params["resource"],
                min_peers_seeing=params["min_peers_seeing"],
            )

    def test__getitem__(self, mock_get):
        response = AnnouncedPrefixes(mock_get.ripestat, 3333)
        assert isinstance(response[0], tuple)  # namedtuple: AnnouncedPrefix

    def test__iter__(self, mock_get):
        response = AnnouncedPrefixes(mock_get.ripestat, 3333)
        assert isinstance(response, Iterable)

    def test__len__(self, mock_get):
        response = AnnouncedPrefixes(mock_get.ripestat, 3333)
        assert len(response) == len(TestAnnouncedPrefixes.RESPONSE["data"]["prefixes"])

    def test_earliest_time(self, mock_get):
        response = AnnouncedPrefixes(mock_get.ripestat, 3333)

        earliest_time = TestAnnouncedPrefixes.RESPONSE["data"]["earliest_time"]
        assert response.earliest_time == datetime.fromisoformat(earliest_time)

    def test_latest_time(self, mock_get):
        response = AnnouncedPrefixes(mock_get.ripestat, 3333)

        latest_time = TestAnnouncedPrefixes.RESPONSE["data"]["latest_time"]
        assert response.latest_time == datetime.fromisoformat(latest_time)

    def test_prefixes(self, mock_get):
        for network in AnnouncedPrefixes(mock_get.ripestat, 3333):
            assert isinstance(network.prefix, ipaddress.IPv4Network)

            for timeline in network.timelines:
                assert isinstance(timeline.starttime, datetime)
                assert isinstance(timeline.endtime, datetime)

    def test_query_endtime(self, mock_get):
        response = AnnouncedPrefixes(mock_get.ripestat, 3333)

        time = TestAnnouncedPrefixes.RESPONSE["data"]["query_endtime"]
        assert response.query_endtime == datetime.fromisoformat(time)

    def test_query_starttime(self, mock_get):
        response = AnnouncedPrefixes(mock_get.ripestat, 3333)

        time = TestAnnouncedPrefixes.RESPONSE["data"]["query_starttime"]
        assert response.query_starttime == datetime.fromisoformat(time)

    def test_resource(self, mock_get):
        response = AnnouncedPrefixes(mock_get.ripestat, 3333)

        resource = TestAnnouncedPrefixes.RESPONSE["data"]["resource"]
        assert response.resource == int(resource)
