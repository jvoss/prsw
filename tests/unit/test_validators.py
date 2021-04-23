"""Test validations used in API endpoints."""

import pytest
import ipaddress

from . import UnitTest
from prsw.validators import Validators


class TestValidators(UnitTest):
    def test__validate_asn(self):
        assert Validators._validate_asn(1234) is True

        with pytest.raises(ValueError):
            Validators._validate_asn(-1)

        with pytest.raises(ValueError):
            Validators._validate_asn(4294967296)

    def test__validate_ip_address(self):
        ipv4_address = ipaddress.IPv4Address("192.168.0.0")
        ipv6_address = ipaddress.IPv6Address("2001:1000::1")

        assert Validators._validate_ip_address(ipv4_address) is True
        assert Validators._validate_ip_address(str(ipv4_address)) is True
        assert Validators._validate_ip_address(ipv6_address) is True
        assert Validators._validate_ip_address(str(ipv6_address)) is True

        with pytest.raises(ValueError):
            Validators._validate_ip_address("invalid")

    def test__validate_ip_network(self):
        ipv4_network = ipaddress.IPv4Network("192.168.0.0/24")
        ipv6_network = ipaddress.IPv6Network("2001:1000::/64")

        assert Validators._validate_ip_network(ipv4_network) is True
        assert Validators._validate_ip_network(str(ipv4_network)) is True
        assert Validators._validate_ip_network(ipv6_network) is True
        assert Validators._validate_ip_network(str(ipv6_network)) is True

        with pytest.raises(ValueError):
            Validators._validate_ip_network("invalid")
