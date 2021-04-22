"""Test prsw.stat.asn_neighbours."""

import pytest
from datetime import datetime
from typing import Iterable
from unittest.mock import patch

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.asn_neighbours import ASNNeighbours


class TestASNNeighbours(UnitTest):
    RESPONSE = {
        "messages": [],
        "see_also": [],
        "version": "4.1",
        "data_call_status": "supported - connecting to Ursa",
        "cached": False,
        "data": {
            "query_time": "2011-12-01T08:00:00",
            "neighbours": [
                {
                    "asn": 1853,
                    "position": "left",
                    "details": {
                        "peer_count": {"v4": 288, "v6": 0},
                        "path_count": 81,
                        "paths": [
                            {
                                "path": "1103 20965 1853 1205",
                                "locations": {
                                    "v4": [{"location": "rrc03", "peer_count": 3}],
                                    "v6": [],
                                },
                            },
                        ],
                    },
                },
            ],
            "neighbour_counts": {"left": 1, "right": 0, "uncertain": 1, "unique": 2},
            "resource": "1205",
            "lod": 1,
            "latest_time": "2021-04-22T00:00:00",
            "earliest_time": "2014-07-01T00:00:00",
        },
        "query_id": "20210422200440-eff7ae1f-de59-4dfd-bd45-26ddb220ca38",
        "process_time": 26,
        "server_id": "app121",
        "build_version": "live.2021.4.19.159",
        "status": "ok",
        "status_code": 200,
        "time": "2021-04-22T20:04:40.611329",
    }

    def setup(self):
        url = f"{API_URL}{ASNNeighbours.PATH}data.json?resource=1205"

        self.api_response = Output(url, **TestASNNeighbours.RESPONSE)
        self.params = {
            "preferred_version": ASNNeighbours.VERSION,
            "resource": "1205",
            "lod": "0",
        }

        return super().setup()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called_with(ASNNeighbours.PATH, self.params)

    def test__init__valid_resource(self, mock_get):
        response = ASNNeighbours(mock_get.ripestat, resource=self.params["resource"])
        assert isinstance(response, ASNNeighbours)

    def test__init__invalid_resource(self, mock_get):
        with pytest.raises(ValueError):
            ASNNeighbours(mock_get.ripestat, resource="invalid")

    def test__init__valid_lod(self, mock_get):
        params = self.params.copy()
        params["lod"] = 0

        response = ASNNeighbours(
            mock_get.ripestat,
            resource=params["resource"],
            lod=params["lod"],
        )

        assert isinstance(response, ASNNeighbours)

        expected_params = params.copy()
        expected_params["lod"] = "0"
        mock_get.params = expected_params

    def test__init__invalid_lod(self, mock_get):
        params = self.params.copy()
        params["lod"] = "invalid"

        with pytest.raises(ValueError):
            ASNNeighbours(
                mock_get.ripestat, resource=params["resource"], lod=params["lod"]
            )

    def test__init__valid_query_time(self, mock_get):
        params = self.params.copy()
        params["query_time"] = datetime.now()

        response = ASNNeighbours(
            mock_get.ripestat,
            resource=params["resource"],
            query_time=params["query_time"],
        )

        assert isinstance(response, ASNNeighbours)

        expected_params = params.copy()
        expected_params["query_time"] = params["query_time"].isoformat()
        mock_get.params = expected_params

    def test__init__invalid_query_time(self, mock_get):
        params = self.params.copy()
        params["query_time"] = "invalid"

        with pytest.raises(ValueError):
            ASNNeighbours(
                mock_get.ripestat,
                resource=params["resource"],
                query_time=params["query_time"],
            )

    def test__iter__(self, mock_get):
        response = ASNNeighbours(mock_get.ripestat, 3333)
        assert isinstance(response, Iterable)

    def test__len__(self, mock_get):
        response = ASNNeighbours(mock_get.ripestat, 3333)
        assert len(response) == len(TestASNNeighbours.RESPONSE["data"]["neighbours"])

    def test__objectify_neighbours(self, mock_get):
        response = ASNNeighbours(mock_get.ripestat, 3333)

        for neighbour in response:
            assert isinstance(neighbour, tuple)  # namedtuple: ASNNeighbour
            assert "asn" in neighbour.__dir__()
            assert "position" in neighbour.__dir__()
            assert "details" in neighbour.__dir__()

            if neighbour.details is not None:
                assert "peer_count" in neighbour.details
                assert "path_count" in neighbour.details
                assert "paths" in neighbour.details

                for path in neighbour.details["paths"]:
                    assert isinstance(path, tuple)  # namedtuple: ASNNeighbourPath
                    assert isinstance(path.paths, tuple)
                    assert isinstance(path.locations, dict)

    def test_earliest_time(self, mock_get):
        mock_get.params = self.params  # reset params
        response = ASNNeighbours(mock_get.ripestat, 1205)

        earliest_time = TestASNNeighbours.RESPONSE["data"]["earliest_time"]
        assert response.earliest_time == datetime.fromisoformat(earliest_time)

    def test_latest_time(self, mock_get):
        mock_get.params = self.params  # reset params
        response = ASNNeighbours(mock_get.ripestat, 1205)

        latest_time = TestASNNeighbours.RESPONSE["data"]["latest_time"]
        assert response.latest_time == datetime.fromisoformat(latest_time)

    def test_neighbors(self, mock_get):
        mock_get.params = self.params  # reset params
        response = ASNNeighbours(mock_get.ripestat, 1205)

        assert isinstance(response.neighbours, list)

        for neighbour in response.neighbours:
            assert isinstance(neighbour, tuple)  # namedtuple: ASNNeighbour

    def test_neighbor_counts(self, mock_get):
        mock_get.params = self.params  # reset params
        response = ASNNeighbours(mock_get.ripestat, 1205)

        counts = response.neighbour_counts

        assert isinstance(counts, tuple)  # namedtuple
        assert isinstance(counts.left, int)
        assert isinstance(counts.right, int)
        assert isinstance(counts.uncertain, int)
        assert isinstance(counts.unique, int)

    def test_query_time(self, mock_get):
        mock_get.params = self.params  # reset params
        response = ASNNeighbours(mock_get.ripestat, 1205)

        query_time = TestASNNeighbours.RESPONSE["data"]["query_time"]
        assert response.query_time == datetime.fromisoformat(query_time)

    def test_resource(self, mock_get):
        mock_get.params = self.params  # reset params
        response = ASNNeighbours(mock_get.ripestat, 1205)

        resource = TestASNNeighbours.RESPONSE["data"]["resource"]
        assert response.resource == int(resource)
