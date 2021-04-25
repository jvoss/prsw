"""Provides the Looking Glass endpoint."""

import ipaddress

from collections import namedtuple
from datetime import datetime

from prsw.validators import Validators


class LookingGlass:
    """
    This data call returns information commonly coming from a Looking Glass.
    The data is based on a data feed from the RIPE NCC's network of BGP route
    collectors (RIS, see `<https://www.ripe.net/data-tools/stats/ris>`_ for more
    information). The data processing usually happens with a small delay and can
    be considered near real-time. The output is structured by collector node (RRC)
    accompanied by the location and the BGP peers which provide the routing
    information.

    Reference: `<https://stat.ripe.net/docs/data_api#looking-glass>`_

    ================    =============================================================
    Property            Description
    ================    =============================================================
    ``latest_time``     Provides **datetime** on how recent this data is.
    ``query_time``      Provides **datetime** on when the query was performed.
    ``peers``           **List** containing all peers from every collector node (RRC)
    ``rrcs``            **Dict** containing each collector node (RRC)
    ================    =============================================================

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()
        result = ripe.looking_glass('140.78.0.0/16')

        for collector in result:
            # RRC(rrc='RRC00', location='Amsterdam, Netherlands', peers=[...])

            print(collector.rrc)
            print(collector.location)

            for peer in collector.peers:
                # Peer(
                #   asn_origin=1205,
                #   as_path=(34854, 6939, 1853, 1853, 1205),
                #   community=['34854:1009'],
                #   last_updated=datetime.datetime(2021, 4, 13, 22, 48, 26),
                #   prefix=IPv4Network('140.78.0.0/16'),
                #   peer=IPv4Address('2.56.11.1'), origin='IGP',
                #   next_hop=IPv4Address('2.56.11.1'),
                #   latest_time=datetime.datetime(2021, 4, 14, 12, 54, 37)
                # )

                print(
                    peer.asn_origin,
                    peer.as_path,
                    peer.community,
                    peer.last_update,
                    peer.prefix,
                    peer.peer,
                    peer.origin,
                    peer.next_hop,
                    peer.latest_time
                )
    """

    PATH = "/looking-glass"
    VERSION = "2.1"

    def __init__(self, RIPEstat, resource: ipaddress.ip_network):
        """
        Initialize and request prefix from the Looking Glass.

        :param resource: A prefix or an IP address. Prefixes need to match exactly a
            prefix found in the routing data. If given as IP address, the data call
            will try to find the encompassing prefix for the IP address.

        """
        # validate and sanitize prefix (ensure proper boundary)
        if Validators._validate_ip_network(resource):
            resource = ipaddress.ip_network(str(resource), strict=False)
        else:
            raise ValueError("resource must be valid IP address or network")

        params = {"preferred_version": LookingGlass.VERSION, "resource": str(resource)}

        self._api = RIPEstat._get(LookingGlass.PATH, params)
        self._rrcs = self._objectify_rrcs(self._api.data["rrcs"])

    def __getitem__(self, rrc):
        """
        Return the collector node specified.

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            rrcs = ripe.looking_glass('140.78.0.0/16')

            rrc = rrcs['RRC00']
            print(rrc.location)

            for peer in rrc.peers:
                print(peer.as_path)

        """
        return self.rrcs[rrc]

    def __iter__(self):
        """
        Provide a way to iterate over each collector node (RRC).

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            rrcs = ripe.looking_glass('140.78.0.0/16')

            for collector in rrcs:
                print(collector.rrc, collector.location, collector.peers)

        """
        for collector in self.rrcs.values():
            yield collector

    def __len__(self):
        """
        Get the number of collector nodes (RRC)

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            rrcs = ripe.looking_glass('140.78.0.0/16')

            print(len(rrcs))

        """
        return len(self.rrcs)

    def _objectify_rrcs(self, list):
        """Processes RRCs from API response."""

        rrcs = {}

        RRC = namedtuple("RRC", ["rrc", "location", "peers"])
        Peer = namedtuple(
            "Peer",
            [
                "asn_origin",
                "as_path",
                "community",
                "last_updated",
                "prefix",
                "peer",
                "origin",
                "next_hop",
                "latest_time",
            ],
        )

        for rrc in list:
            peers = []

            # repack peers with python objects
            for peer in rrc["peers"]:
                t_peer = {}
                t_peer["asn_origin"] = int(peer["asn_origin"])
                t_peer["as_path"] = tuple(map(int, peer["as_path"].split(" ")))
                t_peer["community"] = str(peer["community"]).split(" ")
                t_peer["last_updated"] = datetime.fromisoformat(peer["last_updated"])
                t_peer["prefix"] = ipaddress.ip_network(peer["prefix"])
                t_peer["peer"] = ipaddress.ip_address(peer["peer"])
                t_peer["origin"] = str(peer["origin"])
                t_peer["next_hop"] = ipaddress.ip_address(peer["next_hop"])
                t_peer["latest_time"] = datetime.fromisoformat(peer["latest_time"])

                peers.append(Peer(**t_peer))

            rrc = rrc.copy()
            rrc["peers"] = peers
            rrcs[rrc["rrc"]] = RRC(**rrc)

        return rrcs

    @property
    def latest_time(self):
        """Provides **datetime** on how recent the data is."""
        return datetime.fromisoformat(self._api.data["latest_time"])

    @property
    def query_time(self):
        """Provides **datetime** on when the query was performed."""
        return datetime.fromisoformat(self._api.data["query_time"])

    @property
    def peers(self):
        """
        Shortcut to a **list** containing all peers from every collector node (RRC).

        Each peer entry is a *Peer* named tuple with the following properties:

        ================    =============================================================
        Property            Description
        ================    =============================================================
        ``asn_origin``      The originating ASN for the matched prefix (**int**)
        ``as_path``         The path of ASNs seen for this route (**tuple**)
        ``community``       BGP community information for this route (**list**)
        ``last_updated``    The timestamp when this route was last changed (**datetime**)
        ``prefix``          The matched prefix (**IPv4Network** or **IPv6Network**) based
                            on the query input resource
        ``peer``            **IPv4Address** or **IPv6Address** of the peer interface
        ``nexthop``         The next hop (**IPv4Address** or **IPv6Address**) from the
                            perspective of this peer
        ``latest_time``     The **datetime** when this route was last confirmed
        ================    =============================================================

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            rrcs = ripe.looking_glass('140.78.0.0/16')

            for peer in rrcs.peers:
                print(peer.as_path)

        """
        peers = []

        for rrc in self.rrcs.values():
            peers += rrc.peers

        return peers

    @property
    def rrcs(self):
        """
        **Dict** containing one entry for each collector node (RRC) that provides
        data for the given input resource. Each RRC entry holds the location and
        the ID of the RRC together with the list of BGP peer information.

        Each value is an RRC *named tuple* with the following properties:

        ============    =======================================================
        Property        Description
        ============    =======================================================
        ``rrc``         ID of the RRC (**str**), "RRC00"
        ``location``    Location of the RRC (**str**), "Amsterdam, Netherlands"
        ``peers``       **List** of BGP peer information, see `peers`
        ============    =======================================================

        """
        return self._rrcs
