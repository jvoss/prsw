"""Provides validators for init arguments in API endpoint classes."""

import ipaddress


class Validators:
    """Validators used for validating arguments in initializers for API endpoints."""

    def _validate_asn(asn: str) -> bool:
        """Validate argument is a valid Autonomous System Number."""

        min = 0
        max = 4294967295

        if int(asn) in range(min, max):
            pass
        else:
            raise ValueError(f"ASN expected to be int between {min} and {max}")

        return True

    def _validate_ip_address(ip: str) -> bool:
        """Validate argument is a valid IPv4 or IPv6 address."""

        ipaddress.ip_address(str(ip))
        return True

    def _validate_ip_network(ip: str, strict=False) -> bool:
        """Validate argument is a valid IPv4 or IPv6 network."""

        ipaddress.ip_network(str(ip), strict=strict)
        return True
