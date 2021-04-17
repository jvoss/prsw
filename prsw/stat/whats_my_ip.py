"""Provides the Whats My Ip endpoint."""

import ipaddress


class WhatsMyIp:
    """
    This data call returns the IP address of the requestor.

    Reference: `<https://stat.ripe.net/docs/data_api#whats-my-ip>`_

    ========= ===============================
    Property  Description
    ========= ===============================
    ``ip``    The IP address of the requestor
    ========= ===============================

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()
        response = ripe.whats_my_ip()

        print(response)
        # '1.1.1.1'

        response.ip
        # IPv4Address('1.1.1.1')
        # -- or depending:
        # IPv6Address('f17d:36e:9d3b:4b39:b3c4:44a:b2b1:45e1')

    """

    PATH = "/whats-my-ip"
    VERSION = "0.1"

    def __init__(self, RIPEstat) -> None:
        """Initialize and request Whats My Ip."""
        params = {"preferred_version": WhatsMyIp.VERSION}
        self._api = RIPEstat._get(WhatsMyIp.PATH, params)

    def __str__(self) -> str:
        """Return the IP address as a String."""
        return str(self.ip)

    @property
    def ip(self):
        """Return the IP address as an **ipaddress** object."""
        return ipaddress.ip_address(self._api.data["ip"])
