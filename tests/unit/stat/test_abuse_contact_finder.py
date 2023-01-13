"""Test prsw.stat.abuse_contact_finder."""

import ipaddress
import pytest
from datetime import datetime
from unittest.mock import patch

from .. import UnitTest

from prsw.api import API_URL, Output
from prsw.stat.abuse_contact_finder import AbuseContactFinder


class TestAbuseContactFinder(UnitTest):
    RESPONSE = {
        "messages": [],
        "see_also": [],
        "version": "2.1",
        "data_call_name": "abuse-contact-finder",
        "data_call_status": "supported",
        "cached": False,
        "data": {
            "abuse_contacts": ["abuse@ripe.net"],
            "authoritative_rir": "ripe",
            "latest_time": "2023-01-13T17:04:58",
            "earliest_time": "2023-01-13T17:04:58",
            "parameters": {"resource": "3333", "cache": "null"},
        },
        "query_id": "20230113170458-070f3b71-4274-4878-ae2a-f38b0162ded6",
        "process_time": 38,
        "server_id": "app129",
        "build_version": "live.2022.12.15.141",
        "status": "ok",
        "status_code": 200,
        "time": "2023-01-13T17:04:58.660821",
    }

    def setup_method(self):
        url = f"{API_URL}{AbuseContactFinder.PATH}data.json?resource=3333"

        self.api_response = Output(url, **TestAbuseContactFinder.RESPONSE)
        self.params = {
            "preferred_version": AbuseContactFinder.VERSION,
            "resource": "3333",
        }

        return super().setup_method()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup_method()

        with patch.object(self.ripestat, "_get") as mocked_get:
            mocked_get.return_value = self.api_response

            yield self

            mocked_get.assert_called_with(AbuseContactFinder.PATH, self.params)

    def test__init__valid_resource_asn(self, mock_get):
        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert isinstance(response, AbuseContactFinder)

    def test__init__valid_resource_ipv4_address(self, mock_get):
        test_ipv4 = "192.168.1.1"

        params = self.params.copy()
        params["resource"] = test_ipv4

        response = AbuseContactFinder(mock_get.ripestat, params["resource"])
        assert isinstance(response, AbuseContactFinder)

        expected_params = params.copy()
        expected_params["resource"] = test_ipv4
        mock_get.params = expected_params

    def test__init__valid_resource_ipv6_address(self, mock_get):
        test_ipv6 = "2001:1000::1"

        params = self.params.copy()
        params["resource"] = test_ipv6

        response = AbuseContactFinder(mock_get.ripestat, params["resource"])
        assert isinstance(response, AbuseContactFinder)

        expected_params = params.copy()
        expected_params["resource"] = test_ipv6
        mock_get.params = expected_params

    def test__init__valid_resource_ipv4_network(self, mock_get):
        test_ipv4_network = "192.168.1.0/24"

        params = self.params.copy()
        params["resource"] = test_ipv4_network

        response = AbuseContactFinder(mock_get.ripestat, params["resource"])
        assert isinstance(response, AbuseContactFinder)

        expected_params = params.copy()
        expected_params["resource"] = test_ipv4_network
        mock_get.params = expected_params

    def test__init__valid_resource_ipv6_network(self, mock_get):
        test_ipv6_network = "2001:1000::/64"

        params = self.params.copy()
        params["resource"] = test_ipv6_network

        response = AbuseContactFinder(mock_get.ripestat, params["resource"])
        assert isinstance(response, AbuseContactFinder)

        expected_params = params.copy()
        expected_params["resource"] = test_ipv6_network
        mock_get.params = expected_params

    def test__init__invalid_resources(self, mock_get):
        test_resources = [-1, "abcdef"]

        for resource in test_resources:
            with pytest.raises(ValueError):
                AbuseContactFinder(mock_get.ripestat, resource)

    def test_abuse_contacts(self, mock_get):
        mock_get.params = self.params  # reset params

        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert response.abuse_contacts == self.RESPONSE["data"]["abuse_contacts"]

    def test_authoritative_rir(self, mock_get):
        mock_get.params = self.params  # reset params

        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert response.authoritative_rir == self.RESPONSE["data"]["authoritative_rir"]

    def test_earliest_time(self, mock_get):
        response = AbuseContactFinder(mock_get.ripestat, 3333)

        time = TestAbuseContactFinder.RESPONSE["data"]["earliest_time"]
        assert response.earliest_time == datetime.fromisoformat(time)

    def test_latest_time(self, mock_get):
        response = AbuseContactFinder(mock_get.ripestat, 3333)

        time = TestAbuseContactFinder.RESPONSE["data"]["latest_time"]
        assert response.latest_time == datetime.fromisoformat(time)

    def test_resource_asn(self, mock_get):
        mock_get.params = self.params  # reset params

        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert isinstance(response.resource, int)
        assert response.resource == 3333

    def test_resource_ipv4_address(self):
        ipv4_address = ipaddress.IPv4Address("192.168.1.1")

        with patch.object(self.ripestat, "_get") as mocked_get:
            api_response = self.api_response
            api_response.data["parameters"]["resource"] = str(ipv4_address)
            mocked_get.return_value = api_response

            params = self.params.copy()
            params["resource"] = str(ipv4_address)

            response = AbuseContactFinder(self.ripestat, ipv4_address)

            assert isinstance(response.resource, ipaddress.IPv4Address)
            assert response.resource == ipv4_address

            mocked_get.assert_called_with(AbuseContactFinder.PATH, params)

    def test_resource_ipv4_network(self):
        ipv4_network = ipaddress.IPv4Network("192.168.1.0/24")

        with patch.object(self.ripestat, "_get") as mocked_get:
            api_response = self.api_response
            api_response.data["parameters"]["resource"] = str(ipv4_network)
            mocked_get.return_value = api_response

            params = self.params.copy()
            params["resource"] = str(ipv4_network)

            response = AbuseContactFinder(self.ripestat, ipv4_network)

            assert isinstance(response.resource, ipaddress.IPv4Network)
            assert response.resource == ipv4_network

            mocked_get.assert_called_with(AbuseContactFinder.PATH, params)

    def test_resource_ipv6_address(self):
        ipv6_address = ipaddress.IPv6Address("2001:1212::1")

        with patch.object(self.ripestat, "_get") as mocked_get:
            api_response = self.api_response
            api_response.data["parameters"]["resource"] = str(ipv6_address)
            mocked_get.return_value = api_response

            params = self.params.copy()
            params["resource"] = str(ipv6_address)

            response = AbuseContactFinder(self.ripestat, ipv6_address)

            assert isinstance(response.resource, ipaddress.IPv6Address)
            assert response.resource == ipv6_address

            mocked_get.assert_called_with(AbuseContactFinder.PATH, params)

    def test_resource_ipv6_network(self):
        ipv6_network = ipaddress.IPv6Network("2001:1212::/64")

        with patch.object(self.ripestat, "_get") as mocked_get:
            api_response = self.api_response
            api_response.data["parameters"]["resource"] = str(ipv6_network)
            mocked_get.return_value = api_response

            params = self.params.copy()
            params["resource"] = str(ipv6_network)

            response = AbuseContactFinder(self.ripestat, ipv6_network)

            assert isinstance(response.resource, ipaddress.IPv6Network)
            assert response.resource == ipv6_network

            mocked_get.assert_called_with(AbuseContactFinder.PATH, params)
