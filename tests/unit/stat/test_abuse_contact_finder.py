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
        "version": "1.2",
        "data_call_status": "supported - connecting to flow",
        "cached": False,
        "data": {
            "query_time": "2021-04-23T16:11:00",
            "resource": "3333",
            "authorities": ["ripe"],
            "blocklist_info": [],
            "global_network_info": {
                "description": "Assigned by RIPE NCC",
                "source": "IANA 16-bit Autonomous System (AS) Numbers Registry",
                "source_url": "http://www.iana.org/assignments/as-numbers/as-numbers-1.csv",
                "name": "Assigned by RIPE NCC",
            },
            "anti_abuse_contacts": {
                "emails": [],
                "objects_with_remarks": [],
                "extracted_emails": [],
                "abuse_c": [
                    {
                        "description": "abuse-c",
                        "email": "abuse@ripe.net",
                        "key": "OPS4-RIPE",
                    }
                ],
            },
            "holder_info": {
                "name": "RIPE-NCC-AS - Reseaux IP Europeens Network Coordination Centre (RIPE NCC)",
                "resource": "3333",
            },
            "special_resources": [],
            "more_specifics": [
                "193.0.18.0-193.0.21.255",
                "193.0.0.0-193.0.23.255",
                "193.0.0.0/16",
            ],
            "less_specifics": [
                "193.0.0.0-193.0.255.255",
                "193.0.0.0-193.0.50.255",
                "193.0.0.0/12",
            ],
        },
        "query_id": "20210423161144-195e9d63-d139-4fab-a8e3-76f2cf41fcs7",
        "process_time": 363,
        "server_id": "app130",
        "build_version": "live.2021.4.19.159",
        "status": "ok",
        "status_code": 200,
        "time": "2021-04-23T15:11:42.851891",
    }

    def setup(self):
        url = f"{API_URL}{AbuseContactFinder.PATH}data.json?resource=3333"

        self.api_response = Output(url, **TestAbuseContactFinder.RESPONSE)
        self.params = {
            "preferred_version": AbuseContactFinder.VERSION,
            "resource": "3333",
        }

        return super().setup()

    @pytest.fixture(scope="session")
    def mock_get(self):
        self.setup()

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

    def test_anti_abuse_contacts(self, mock_get):
        mock_get.params = self.params  # reset params

        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert isinstance(response.anti_abuse_contacts, tuple)  # namedtuple
        assert "abuse_c" in response.anti_abuse_contacts.__dir__()
        assert "emails" in response.anti_abuse_contacts.__dir__()
        assert "objects_with_remarks" in response.anti_abuse_contacts.__dir__()
        assert "extracted_emails" in response.anti_abuse_contacts.__dir__()

        expected_abuse_c = self.RESPONSE["data"]["anti_abuse_contacts"]["abuse_c"]
        assert response.anti_abuse_contacts.abuse_c == expected_abuse_c

    def test_authorities(self, mock_get):
        mock_get.params = self.params  # reset params

        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert isinstance(response.authorities, list)
        assert response.authorities == self.RESPONSE["data"]["authorities"]

    def test_blocklist_info(self, mock_get):
        mock_get.params = self.params  # reset params

        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert isinstance(response.blocklist_info, list)
        assert response.blocklist_info == self.RESPONSE["data"]["blocklist_info"]

    def test_global_network_info(self, mock_get):
        mock_get.params = self.params  # reset params

        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert isinstance(response.global_network_info, tuple)  # namedtuple

        properties = ["description", "name", "source", "source_url"]
        for property in properties:
            assert property in response.global_network_info.__dir__()

    def test_holder_info(self, mock_get):
        mock_get.params = self.params  # reset params

        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert isinstance(response.holder_info, tuple)  # namedtuple
        assert "name" in response.holder_info.__dir__()
        assert "resource" in response.holder_info.__dir__()

        expected_name = self.RESPONSE["data"]["holder_info"]["name"]
        expected_resource = self.RESPONSE["data"]["holder_info"]["resource"]

        assert response.holder_info.name == expected_name
        assert response.holder_info.resource == expected_resource

    def test_less_specific(self, mock_get):
        response = AbuseContactFinder(mock_get.ripestat, 3333)

        assert isinstance(response.more_specifics, list)
        assert response.less_specifics == self.RESPONSE["data"]["less_specifics"]

    def test_more_specific(self, mock_get):
        response = AbuseContactFinder(mock_get.ripestat, 3333)

        assert isinstance(response.more_specifics, list)
        assert response.more_specifics == self.RESPONSE["data"]["more_specifics"]

    def test_query_time(self, mock_get):
        response = AbuseContactFinder(mock_get.ripestat, 3333)

        time = TestAbuseContactFinder.RESPONSE["data"]["query_time"]
        assert response.query_time == datetime.fromisoformat(time)

    def test_resource_asn(self, mock_get):
        mock_get.params = self.params  # reset params

        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert isinstance(response.resource, int)
        assert response.resource == 3333

    def test_resource_ipv4_address(self):
        ipv4_address = ipaddress.IPv4Address("192.168.1.1")

        with patch.object(self.ripestat, "_get") as mocked_get:
            api_response = self.api_response
            api_response.data["resource"] = str(ipv4_address)
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
            api_response.data["resource"] = str(ipv4_network)
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
            api_response.data["resource"] = str(ipv6_address)
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
            api_response.data["resource"] = str(ipv6_network)
            mocked_get.return_value = api_response

            params = self.params.copy()
            params["resource"] = str(ipv6_network)

            response = AbuseContactFinder(self.ripestat, ipv6_network)

            assert isinstance(response.resource, ipaddress.IPv6Network)
            assert response.resource == ipv6_network

            mocked_get.assert_called_with(AbuseContactFinder.PATH, params)

    def test_special_resources(self, mock_get):
        mock_get.params = self.params  # reset params

        response = AbuseContactFinder(mock_get.ripestat, 3333)
        assert isinstance(response.special_resources, list)
        assert response.special_resources == self.RESPONSE["data"]["special_resources"]
