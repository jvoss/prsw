"""Test prsw.stat.address_space_hierarchy."""

import pytest
import ipaddress
from datetime import datetime
from typing import Iterable
from unittest.mock import patch

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.address_space_hierarchy import AddressSpaceHierarchy


class TestAddressSpaceHierarchy(UnitTest):

    RESPONSE = {
        "messages": [],
        "see_also": [],
        "version": "1.3",
        "data_call_name": "address-space-hierarchy",
        "data_call_status": "supported",
        "cached": False,
        "data": {
            "rir": "ripe",
            "resource": "193.0.0.0/21",
            "exact": [
                {
                    "inetnum": "193.0.0.0 - 193.0.7.255",
                    "netname": "RIPE-NCC",
                    "descr": "RIPE Network Coordination Centre, Amsterdam, Netherlands",
                    "org": "ORG-RIEN1-RIPE",
                    "remarks": "Used for RIPE NCC infrastructure.",
                    "country": "NL",
                    "admin-c": "BRD-RIPE",
                    "tech-c": "OPS4-RIPE",
                    "status": "ASSIGNED PA",
                    "mnt-by": "RIPE-NCC-MNT",
                    "created": "2003-03-17T12:15:57Z",
                    "last-modified": "2017-12-04T14:42:31Z",
                    "source": "RIPE",
                }
            ],
            "less_specific": [
                {
                    "inetnum": "193.0.0.0 - 193.0.23.255",
                    "netname": "NL-RIPENCC-OPS-990305",
                    "country": "NL",
                    "org": "ORG-RIEN1-RIPE",
                    "admin-c": "BRD-RIPE",
                    "tech-c": "OPS4-RIPE",
                    "status": "ALLOCATED PA",
                    "remarks": "Amsterdam, Netherlands",
                    "mnt-by": "RIPE-NCC-HM-MNT, RIPE-NCC-MNT",
                    "mnt-routes": "RIPE-NCC-MNT, RIPE-GII-MNT { 193.0.8.0/23 }",
                    "created": "2012-03-09T15:03:38Z",
                    "last-modified": "2024-07-24T15:35:02Z",
                    "source": "RIPE",
                }
            ],
            "more_specific": [],
            "query_time": "2024-10-10T14:42:39",
            "parameters": {"resource": "193.0.0.0/21", "cache": None},
        },
        "query_id": "20241010144239-e4fea150-ac7e-4ad4-94e3-1207a9c00f73",
        "process_time": 60,
        "server_id": "app127",
        "build_version": "live.2024.9.25.217",
        "status": "ok",
        "status_code": 200,
        "time": "2024-10-10T14:42:39.989690",
    }

    def setup_method(self):
        url = f"{API_URL}{AddressSpaceHierarchy.PATH}data.json?resource=193.0.0.0/21"

        self.api_response = Output(url, **TestAddressSpaceHierarchy.RESPONSE)
        self.params = {
            "preferred_version": AddressSpaceHierarchy.VERSION,
            "resource": "193.0.0.0/21",
        }

        return super().setup_method()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup_method()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called_with(AddressSpaceHierarchy.PATH, self.params)

    def test__init__valid_resource(self, mock_get):
        response = AddressSpaceHierarchy(mock_get.ripestat, "193.0.0.0/21")
        assert isinstance(response, AddressSpaceHierarchy)

    def test__init__invalid_resource(self):
        with pytest.raises(ValueError):
            AddressSpaceHierarchy(self.ripestat, resource="invalid")

    def test_resource(self, mock_get):
        response = AddressSpaceHierarchy(
            mock_get.ripestat,
            resource=self.params["resource"],
        )

        assert isinstance(response.resource, ipaddress.IPv4Network)
        assert response.resource == ipaddress.ip_network(self.params["resource"])

    def test_exact_inetnums(self, mock_get):
        response = AddressSpaceHierarchy(
            mock_get.ripestat, resource=self.params["resource"]
        )

        assert isinstance(response.exact_inetnums, Iterable)

    def test_more_specific_inetnums(self, mock_get):
        response = AddressSpaceHierarchy(
            mock_get.ripestat, resource=self.params["resource"]
        )

        assert isinstance(response.more_specific_inetnums, Iterable)

    def test_less_specific_inetnums(self, mock_get):
        response = AddressSpaceHierarchy(
            mock_get.ripestat, resource=self.params["resource"]
        )

        assert isinstance(response.less_specific_inetnums, Iterable)

    def test_rir(self, mock_get):
        response = AddressSpaceHierarchy(
            mock_get.ripestat, resource=self.params["resource"]
        )

        assert isinstance(response.rir, str)

    def test_query_time(self, mock_get):
        response = AddressSpaceHierarchy(mock_get.ripestat, "193.0.0.0/21")
        assert isinstance(response.query_time, datetime)

        query_time = self.RESPONSE["data"]["query_time"]
        assert response.query_time == datetime.fromisoformat(query_time)
