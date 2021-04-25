"""Provides the Network Info endpoint."""

import ipaddress

from prsw.validators import Validators


class NetworkInfo:
    """
    This data call returns the containing prefix and announcing ASN of a given IP
    address.

    Reference: '<https://stat.ripe.net/docs/data_api#network-info>'_

    ==========  ===============================================================
    Property    Description
    ==========  ===============================================================
    ``asns``    List of ASNs the prefix is announced from
    ``prefix``  IPAddress containing the prefix the requessted IP address is in
    ==========  ===============================================================

    .. code-block:: python

        ripe = prsw.RIPEstat()
        response = ripe.network_info('140.78.90.50')

        for asn in response.asns:
            print(asn)
            # 5511
            # 6453

        reponse.asns
        # [5511, 6453]

        print(response.prefix)
        # '140.78.0.0/16'

        response.prefix
        # IPv4Network('140.78.0.0/16')

    """

    PATH = "/network-info"
    VERSION = "1.0"

    def __init__(self, RIPEstat, resource: ipaddress.ip_address):
        """
        Initialize and request Network Info.

        :param resource: Any IP address one wants to get network info for
        """
        # validate resource as valid IP address
        if Validators._validate_ip_address(resource):
            resource = ipaddress.ip_address(str(resource))
        else:
            raise ValueError("resource must be a valid IP address")

        params = {"preferred_version": NetworkInfo.VERSION, "resource": str(resource)}

        self._api = RIPEstat._get(NetworkInfo.PATH, params)

    @property
    def asns(self):
        """Return a list of ASNs the prefix is announced from."""
        return list(map(int, self._api.data["asns"]))

    @property
    def prefix(self):
        """Return the prefix the requested IP address is in."""
        return ipaddress.ip_network(self._api.data["prefix"])
