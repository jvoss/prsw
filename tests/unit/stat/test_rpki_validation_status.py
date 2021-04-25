"""Test prsw.stat.rpki_validation_status."""

import pytest
from ipaddress import IPv4Network
from typing import Iterable
from unittest.mock import patch

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.rpki_validation_status import RPKIValidationStatus


class TestRPKIValidationStatus(UnitTest):
    RESPONSE = {
        "messages": [],
        "see_also": [],
        "version": "0.2",
        "data_call_status": "supported",
        "cached": False,
        "data": {
            "validating_roas": [
                {
                    "origin": "3333",
                    "prefix": "193.0.0.0/21",
                    "validity": "valid",
                    "source": "RIPE NCC RPKI Root",
                    "max_length": 21,
                }
            ],
            "status": "valid",
            "resource": "3333",
            "prefix": "193.0.0.0/21",
        },
        "query_id": "20210415140248-91994a38-c339-42e1-9928-aa5444c7b34d",
        "process_time": 10,
        "server_id": "app145",
        "build_version": "live.2021.4.14.157",
        "status": "ok",
        "status_code": 200,
        "time": "2021-04-15T12:02:35.628297",
    }

    def setup(self):
        url = f"{API_URL}{RPKIValidationStatus.PATH}data.json?resource=3333&prefix=193.0.0.0/21"

        self.api_response = Output(url, **TestRPKIValidationStatus.RESPONSE)
        self.params = {
            "preferred_version": RPKIValidationStatus.VERSION,
            "resource": "3333",
            "prefix": "193.0.0.0/21",
        }

        return super().setup()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called_with(RPKIValidationStatus.PATH, self.params)

    def test__init__valid_params(self, mock_get):
        response = RPKIValidationStatus(
            mock_get.ripestat,
            resource=self.params["resource"],
            prefix=self.params["prefix"],
        )

        assert isinstance(response, RPKIValidationStatus)

    def test__init__invalid_prefix(self):
        with pytest.raises(ValueError):
            RPKIValidationStatus(
                self.ripestat, resource=self.params["resource"], prefix="invalid"
            )

    def test_prefix(self, mock_get):
        response = RPKIValidationStatus(
            mock_get.ripestat,
            resource=self.params["resource"],
            prefix=self.params["prefix"],
        )

        assert isinstance(response.prefix, IPv4Network)
        assert response.prefix == IPv4Network(self.params["prefix"])

    def test_resource(self, mock_get):
        response = RPKIValidationStatus(
            mock_get.ripestat,
            resource=self.params["resource"],
            prefix=self.params["prefix"],
        )

        assert response.resource == int(self.params["resource"])

    def test_status(self, mock_get):
        response = RPKIValidationStatus(
            mock_get.ripestat,
            resource=self.params["resource"],
            prefix=self.params["prefix"],
        )

        assert response.status == TestRPKIValidationStatus.RESPONSE["data"]["status"]

    def test_validating_roas(self, mock_get):
        response = RPKIValidationStatus(
            mock_get.ripestat,
            resource=self.params["resource"],
            prefix=self.params["prefix"],
        )

        assert isinstance(response.validating_roas, Iterable)

        for roa in response.validating_roas:
            assert "origin" in roa.__dir__()
            assert "prefix" in roa.__dir__()
            assert "validity" in roa.__dir__()
            assert "source" in roa.__dir__()
            assert "max_length" in roa.__dir__()

            assert isinstance(roa.prefix, IPv4Network)
