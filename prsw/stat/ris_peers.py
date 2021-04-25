"""Provides the RIS Peers endpoint."""

import ipaddress

from collections import namedtuple
from datetime import datetime
from typing import Optional

from prsw.validators import Validators


class RISPeers:
    """
    This data call provides information on the peers of RIS - ASN, IP address and
    number of shared routes. The data is grouped by RIS collectors.

    Historical lookups are supported - a query has to be aligned to the times (00:00,
    08:00 and 16:00 UTC) when RIS data has been collected. By default, the data call
    returns the latest data.

    Reference: `<https://stat.ripe.net/docs/data_api#ris-peers>`_

    =================   ==================================================
    Property            Description
    =================   ==================================================
    ``earliest_time``   **datetime** defining the time of the lookup.
    ``latest_time``     **datetime** defining the latest information time.
    ``peers``           **dict** of RRCs (see below)
    ``query_time``      **dict** containing query **datetime** supplied
    =================   ==================================================

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()
        response = ripe.ris_peers()

        for rrc, peers in response.peers.items():
            print(rrc)  # "RRC11"

            for peer in peers:
                print(peer.v6_prefix_count) # 0
                print(peer.ip)              # IPv4Address('198.32.160.121')
                print(peer.asn)             # 10310
                print(peer.v4_prefix_count) # 248

    """

    PATH = "/ris-peers"
    VERSION = "1.0"

    def __init__(self, RIPEstat, query_time: Optional[datetime] = None) -> None:
        """
        Initialize and request RIS Peers.

        :param query_time: Defines the time of the lookup. This value will be
            automatically aligned to a RIS colletion time.

        .. code-block:: python

            from datetime import datetime

            time = datetime.fromisoformat("2021-01-01T16:00:00.000000")

            ripe = prsw.RIPEstat()
            ris_peers = ripe.ris_peers(query_time=time)
        """

        params = {"preferred_version": RISPeers.VERSION}

        if query_time:
            if Validators._validate_datetime(query_time):
                params["query_time"] = query_time.isoformat()
            else:
                raise ValueError("query_time expect to be datetime")

        self._api = RIPEstat._get(RISPeers.PATH, params)

    def __getitem__(self, rrc: str):
        """
        Return the collector node specified.

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            rrcs = ripe.ris_peers()

            rrc = rrcs['RRC00']

            for peer in rrc.peers:
                print(peer.asn)

        """
        return self.peers[rrc]

    def __iter__(self):
        """
        Provides a shortcut to iterate over each peer from all collector nodes.

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            peers = ripe.ris_peers()

            for peer in peers:
                print(peer.asn)
                print(peer.ip)

        """
        for peers in self.peers.values():
            for peer in peers:
                yield peer

    @property
    def earliest_time(self):
        """Earliest **datetime** data is available."""
        return datetime.fromisoformat(self._api.data["earliest_time"])

    @property
    def latest_time(self):
        """Latest **datetime** data is available."""
        return datetime.fromisoformat(self._api.data["latest_time"])

    def keys(self):
        """Returns a list of RRC names in the dataset."""
        return self.peers.keys()

    @property
    def peers(self):
        """
        **dict** containing each RRC (key) with **list** of RISPeers

        RISPeers have the following properties:

        =================== =============================
        Property            Description
        =================== =============================
        ``asn``             Peer Autonomous System number
        ``ip``              Peer IP address
        ``v4_prefix_count`` Count of IPv4 prefixes
        ``v6_prefix_count`` Count of IPv6 prefixes
        =================== =============================

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            rrcs = ripe.ris_peers()

            for rrc, peers in rrcs.peers.items():
                print(rrc) # "RRC11"

                for peer in peers:
                    print(peer.asn)             # 10310
                    print(peer.ip)              # IPv4Address("198.32.160.121")
                    print(peer.v4_prefix_count) # 248
                    print(peer.v6_prefix_count) # 0

        """
        ris_peers = {}
        RISPeer = namedtuple(
            "RISPeer", ["asn", "ip", "v4_prefix_count", "v6_prefix_count"]
        )

        for rrc, peers in self._api.data["peers"].items():
            rrc = str(rrc).upper()
            ris_peers[rrc] = []

            for peer in peers:
                properties = {
                    "asn": int(peer["asn"]),
                    "ip": ipaddress.ip_address(peer["ip"]),
                    "v4_prefix_count": int(peer["v4_prefix_count"]),
                    "v6_prefix_count": int(peer["v6_prefix_count"]),
                }

                ris_peers[rrc].append(RISPeer(**properties))

        return ris_peers

    @property
    def query_time(self):
        """**datetime** of used by query."""
        return datetime.fromisoformat(self._api.data["parameters"]["query_time"])
