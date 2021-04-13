"""Provides the Announced Prefixes endpoint."""

import ipaddress

from collections import namedtuple
from datetime import datetime
from typing import Optional


class AnnouncedPrefixes:
    """
    This data call returns all announced prefixes for a given ASN. The results
    can be restricted to a specific time period.

    Reference: `<https://stat.ripe.net/docs/data_api#announced-prefixes>`_

    ====================    =======================================================
    Attribute               Description
    ====================    =======================================================
    ``resource``            The Autonomous System Number for which to return
                            prefixes
    ``starttime``           The start time for the query. (defaults to two weeks
                            before current date and time)
    ``endtime``             The start time for the query. (defaults to two
                            weeks before current date and time)
    ``min_peers_seeing``    Minimum number of RIS peers seeing the prefix for
                            it to be included in the results. Excludes low
                            visibility/localized announcements. (default 10)
    ====================    =======================================================

    .. code-block:: python

        import rsaw

        prefixes = rsaw.announced_prefixes(3333)

        for network in prefixes:
            print(network.prefix, network.timelines)

    """

    PATH = "/announced-prefixes/"
    VERSION = "1.2"

    def __init__(
        self,
        RIPEstat,
        resource,
        starttime: Optional[datetime] = None,
        endtime: Optional[datetime] = None,
        min_peers_seeing=None,
    ):
        """Initialize and request Announced Prefixes."""

        params = f"preferred_version={AnnouncedPrefixes.VERSION}&"
        params += "resource=" + str(resource)

        if starttime:
            if isinstance(starttime, datetime.datetime):
                params += "&starttime=" + str(starttime)
            else:
                raise ValueError("starttime expected to be datetime")
        if endtime:
            if isinstance(endtime, datetime.datetime):
                params += "&endtime=" + str(endtime)
            else:
                raise ValueError("endtime expected to be datetime")
        if min_peers_seeing:
            if isinstance(min_peers_seeing, int):
                params += "&min_peers_seeing=" + str(min_peers_seeing)
            else:
                raise ValueError("min_peers_seeing expected to be int")

        self._api = RIPEstat._get(AnnouncedPrefixes.PATH, params)

    def __iter__(self):
        """
        Provide a way to iterate over announced prefixes.

        .. code-block:: python

            prefixes = rsaw.announced_prefixes(3333)
            for announced_prefix in prefixes:
                print(announced_prefix.prefix, announced_prefix.timelines)

        """
        for prefix in self.prefixes:
            yield prefix

    def __getitem__(self, index):
        """Get a specific index of the returned anncouned prefixes."""
        return self.prefixes[index]

    def __len__(self):
        """
        Get the number of prefixes in announced prefixes.

        .. code-block:: python

            prefixes = rsaw.announced_prefixes(3333)
            print(len(prefixes))

        """
        return len(self.prefixes)

    @property
    def earliest_time(self):
        """Earliest `datetime` data is available for."""
        return datetime.fromisoformat(self._api.data["earliest_time"])

    @property
    def latest_time(self):
        """Latest `datetime` data is available for."""
        return datetime.fromisoformat(self._api.data["latest_time"])

    @property
    def prefixes(self):
        """A list of all announced prefixes + the timelines when they were visible."""
        prefixes = []
        AnnouncedPrefix = namedtuple("AnnouncedPrefix", ["prefix", "timelines"])

        for prefix in self._api.data["prefixes"]:
            ip_network = ipaddress.ip_network(prefix["prefix"], strict=False)
            timelines = []

            for timeline in prefix["timelines"]:
                for key, time in timeline.items():
                    timelines.append({key: datetime.fromisoformat(time)})

            tuple_data = {"prefix": ip_network, "timelines": timelines}
            prefixes.append(AnnouncedPrefix(**tuple_data))

        return prefixes

    @property
    def query_endtime(self):
        """The `datetime` at which the query ended."""
        return datetime.fromisoformat(self._api.data["query_endtime"])

    @property
    def query_starttime(self):
        """The `datetime` at which the query started."""
        return datetime.fromisoformat(self._api.data["query_starttime"])

    @property
    def resource(self):
        """The resource used for the query."""
        return self._api.data["resource"]
