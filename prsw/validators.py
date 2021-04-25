"""Provides validators for init arguments in API endpoint classes."""

import ipaddress

from datetime import datetime


class Validators:
    """Validators used for validating arguments in initializers for API endpoints."""

    def _validate_asn(asn: str) -> bool:
        """Validate argument is a valid Autonomous System Number."""

        min = 0
        max = 4294967295

        try:
            if int(asn) in range(min, max):
                pass
            else:
                return False
        except ValueError:
            return False

        return True

    def _validate_datetime(datetime_obj) -> bool:
        """Validate object is a datetime."""

        if not isinstance(datetime_obj, datetime):
            return False

        return True

    def _validate_ip_address(ip: str) -> bool:
        """Validate argument is a valid IPv4 or IPv6 address."""

        try:
            ipaddress.ip_address(str(ip))
        except ValueError:
            return False

        return True

    def _validate_ip_network(ip: str, strict=False) -> bool:
        """Validate argument is a valid IPv4 or IPv6 network."""

        try:
            ipaddress.ip_network(str(ip), strict=strict)
        except ValueError:
            return False

        return True
