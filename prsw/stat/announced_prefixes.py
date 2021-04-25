"""Provides the Announced Prefixes endpoint."""

import ipaddress

from collections import namedtuple
from datetime import datetime
from typing import Optional

from prsw.validators import Validators


class AnnouncedPrefixes:
    """
    This data call returns all announced prefixes for a given ASN. The results
    can be restricted to a specific time period.

    Reference: `<https://stat.ripe.net/docs/data_api#announced-prefixes>`_

    =================== ===============================================================
    Property            Description
    =================== ===============================================================
    ``earliest_time``   Earliest **datetime** data is available for.
    ``latest_time``     Latest **datetime** data is available for.
    ``prefixes``        A **list** of all announced prefixes + the timelines when they
                        were visible.
    ``query_endtime``   The **datetime** at which the query ended.
    ``query_starttime`` The **datetime** at which the query started.
    ``resource``        The resource used for the query.
    =================== ===============================================================

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()
        prefixes = ripe.announced_prefixes(3333)

        for network in prefixes:
            # AnnouncedPrefix(
            #   prefix=IPv4Network('193.0.0.0/21'),
            #   timelines=[
            #       Timeline(
            #           starttime=datetime.datetime(2021, 3, 31, 8, 0),
            #           endtime=datetime.datetime(2021, 4, 14, 8, 0)
            #       )
            #   ]
            # )

            print(network.prefix, network.timelines)

    """

    PATH = "/announced-prefixes"
    VERSION = "1.2"

    def __init__(
        self,
        RIPEstat,
        resource,
        starttime: Optional[datetime] = None,
        endtime: Optional[datetime] = None,
        min_peers_seeing=None,
    ):
        """
        Initialize and request Announced Prefixes.

        :param resource: The Autonomous System Number for which to return prefixes
        :param starttime: The start time for the query. (defaults to two weeks before
            current date and time)
        :param endtime: The start time for the query. (defaults to two weeks before
            current date and time)
        :param min_peers_seeing: Minimum number of RIS peers seeing the prefix for
            it to be included in the results. Excludes low visibility/localized
            announcements. (default 10)

        .. code-block:: python

            from datetime import datetime

            start = datetime.fromisoformat("2021-01-01T12:00:00.000000")
            end = datetime.now()

            prefixes = ripe.announced_prefixes(
                3333,                # Autonomous System Number
                starttime=start,     # datetime
                endtime=end,         # datetime
                min_peers_seeing=20, # int
                )

        """

        params = {
            "preferred_version": AnnouncedPrefixes.VERSION,
            "resource": str(resource),
        }

        if starttime:
            if Validators._validate_datetime(starttime):
                params["starttime"] = starttime.isoformat()
            else:
                raise ValueError("starttime expected to be datetime")
        if endtime:
            if Validators._validate_datetime(endtime):
                params["endtime"] = endtime.isoformat()
            else:
                raise ValueError("endtime expected to be datetime")
        if min_peers_seeing:
            if isinstance(min_peers_seeing, int):
                params["min_peers_seeing"] = str(min_peers_seeing)
            else:
                raise ValueError("min_peers_seeing expected to be int")

        self._api = RIPEstat._get(AnnouncedPrefixes.PATH, params)

    def __getitem__(self, index):
        """Get a specific index of the returned anncouned prefixes."""
        return self.prefixes[index]

    def __iter__(self):
        """
        Provide a way to iterate over announced prefixes.

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            prefixes = ripe.announced_prefixes(3333)

            for announced_prefix in prefixes:
                print(announced_prefix.prefix, announced_prefix.timelines)

        """
        return self.prefixes.__iter__()

    def __len__(self):
        """
        Get the number of prefixes in announced prefixes.

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            prefixes = ripe.announced_prefixes(3333)

            print(len(prefixes))

        """
        return len(self.prefixes)

    @property
    def earliest_time(self):
        """Earliest **datetime** data is available for."""
        return datetime.fromisoformat(self._api.data["earliest_time"])

    @property
    def latest_time(self):
        """Latest **datetime** data is available for."""
        return datetime.fromisoformat(self._api.data["latest_time"])

    @property
    def prefixes(self):
        """
        A list of all announced prefixes + the timelines when they were visible.

        Returns a **list** of `AnnouncedPrefix` named tuples with the following
        properties:

        =============   ========================================================
        Property        Description
        =============   ========================================================
        ``prefix``      Announced **IPv4Network** or **IPv6Network**
        ``timelines``   **List** of Timeline named tuples with properties
                        ``starttime`` and ``endtime``
        =============   ========================================================

        """
        prefixes = []
        AnnouncedPrefix = namedtuple("AnnouncedPrefix", ["prefix", "timelines"])
        Timeline = namedtuple("Timeline", ["starttime", "endtime"])

        for prefix in self._api.data["prefixes"]:
            ip_network = ipaddress.ip_network(prefix["prefix"], strict=False)
            timelines = []

            for timeline in prefix["timelines"]:
                starttime = datetime.fromisoformat(timeline["starttime"])
                endtime = datetime.fromisoformat(timeline["endtime"])

                timelines.append(Timeline(starttime=starttime, endtime=endtime))

            tuple_data = {"prefix": ip_network, "timelines": timelines}
            prefixes.append(AnnouncedPrefix(**tuple_data))

        return prefixes

    @property
    def query_endtime(self):
        """The **datetime** at which the query ended."""
        return datetime.fromisoformat(self._api.data["query_endtime"])

    @property
    def query_starttime(self):
        """The **datetime** at which the query started."""
        return datetime.fromisoformat(self._api.data["query_starttime"])

    @property
    def resource(self):
        """The resource, autonomous system number, used for the query."""
        return int(self._api.data["resource"])
