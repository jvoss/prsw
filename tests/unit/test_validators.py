"""Test validations used in API endpoints."""

import datetime
import ipaddress

from . import UnitTest
from prsw.validators import Validators


class TestValidators(UnitTest):
    def test__validate_asn(self):
        assert Validators._validate_asn(1234) is True
        assert Validators._validate_asn(-1) is False
        assert Validators._validate_asn(4294967296) is False

    def test__validate_datetime(self):
        valid_datetime = datetime.datetime.now()
        assert Validators._validate_datetime(valid_datetime) is True
        assert Validators._validate_datetime("invalid") is False

    def test__validate_ip_address(self):
        ipv4_address = ipaddress.IPv4Address("192.168.0.0")
        ipv6_address = ipaddress.IPv6Address("2001:1000::1")

        assert Validators._validate_ip_address(ipv4_address) is True
        assert Validators._validate_ip_address(str(ipv4_address)) is True
        assert Validators._validate_ip_address(ipv6_address) is True
        assert Validators._validate_ip_address(str(ipv6_address)) is True

        assert Validators._validate_ip_address("invalid") is False
        assert Validators._validate_ip_address("192.168.0.0/24") is False
        assert Validators._validate_ip_address("2001:1000::1/64") is False

    def test__validate_ip_network(self):
        ipv4_network = ipaddress.IPv4Network("192.168.0.0/24")
        ipv6_network = ipaddress.IPv6Network("2001:1000::/64")

        assert Validators._validate_ip_network(ipv4_network) is True
        assert Validators._validate_ip_network(str(ipv4_network)) is True
        assert Validators._validate_ip_network(ipv6_network) is True
        assert Validators._validate_ip_network(str(ipv6_network)) is True

        assert Validators._validate_ip_network("invalid") is False
        assert Validators._validate_ip_network("192.168.0.1/24", strict=True) is False
