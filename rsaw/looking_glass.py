"""Provides the Looking Glass endpoint."""

import ipaddress

from collections import namedtuple
from datetime import datetime

from ._api import get


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

    .. code-block:: python

        import rsaw

        result = rsaw.looking_glass('140.78.0.0/16')

        for collector in result:
            print(collector.rrc)
            print(collector.location)

            for peer in collector.peers:
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

    PATH = "/looking-glass/"
    VERSION = "2.1"

    def __init__(self, resource: ipaddress.ip_network):
        """
        Initialize and request prefix from the Looking Glass.

        :param resource: A prefix or an IP address. Prefixes need to match
            exactly a prefix found in the routing data. If given as IP address,
            the data call will try to find the encompassing prefix for the IP address.

        """
        # validate and sanitize prefix (ensure proper boundary)
        resource = ipaddress.ip_network(str(resource), strict=False)

        params = f"preferred_version={LookingGlass.VERSION}&"
        params += "resource=" + str(resource)

        self._api = get(LookingGlass.PATH, params)

    def __iter__(self):
        """
        Provide a way to iterate over each collector node (RRC).

        Example:
        -------
        .. code-block:: python

            rrcs = rsaw.looking_glass('140.78.0.0/16')
            for collector in rrcs:
                print(collector.rrc, collector.location, collector.peers)

        """
        for collector in self.rrcs:
            yield collector

    def __getitem__(self, rrc):
        """
        Return the collector node specified.

        Example:
        -------
        .. code-block:: python

            rrcs = rsaw.looking_glass('140.78.0.0/16')
            rrc = rrcs['RRC00']
            print(rrc.location)

        """
        for v in self.rrcs:
            if v.rrc == rrc:
                return v

    def __len__(self):
        """
        Get the number of collector nodes (RRC)

        Example:
        -------
        .. code-block:: python

            rrcs = rsaw.looking_glass('140.78.0.0/16')
            print(len(rrcs))
        
        """
        return len(self.rrcs())

    @property
    def latest_time(self):
        """Provides `datetime` on how recent the data is."""
        return datetime.fromisoformat(self._api.data["latest_time"])

    @property
    def query_time(self):
        """Provides `datetime` on when the query was performed."""
        return datetime.fromisoformat(self._api.data["latest_time"])

    @property
    def rrcs(self):
        """
        List containing one entry for each collector node (RRC) that provides
        data for the given input resource. Each RRC entry holds the location and
        the ID of the RRC together with the list of BGP peer information.
        """
        rrcs = []

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

        for rrc in self._api.data["rrcs"]:
            peers = []
            rrc = rrc.copy()

            # repack peers with python objects
            for peer in rrc["peers"]:
                peer = peer.copy()

                peer["asn_origin"] = int(peer["asn_origin"])
                peer["as_path"] = tuple(map(int, peer["as_path"].split(" ")))
                peer["community"] = str(peer["community"]).split(" ")
                peer["last_updated"] = datetime.fromisoformat(peer["last_updated"])
                peer["prefix"] = ipaddress.ip_network(peer["prefix"])
                peer["peer"] = ipaddress.ip_address(peer["peer"])
                peer["origin"] = str(peer["origin"])
                peer["next_hop"] = ipaddress.ip_address(peer["next_hop"])
                peer["latest_time"] = datetime.fromisoformat(peer["latest_time"])

                peers.append(Peer(**peer))

            rrc["peers"] = peers
            rrcs.append(RRC(**rrc))

        return rrcs
