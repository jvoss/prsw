"""Provides the Routing History endpoint."""

import ipaddress

from collections import namedtuple
from datetime import datetime
from typing import Optional

from prsw.validators import Validators


class RoutingHistory:
    """
    This data call shows the history of announcements for prefixes, including the origin ASN and the first hop.

    Reference: `<https://stat.ripe.net/docs/data_api#routing-history>`_

    =================== ===============================================================
    Property            Description
    =================== ===============================================================
    ``by_origin`` A list containing routes grouped by origin.
    ``query_endtime``   The **datetime** at which the query ended.
    ``query_starttime`` The **datetime** at which the query started.
    ``resource``        The resource used for the query / prefix or ASN
    =================== ===============================================================

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()
        history = ripe.routing_history(3333)

        for element in history:
            print(element.prefix, element.timelines)

    """

    PATH = "/routing-history"
    VERSION = "2.3"

    def __init__(
        self,
        RIPEstat,
        resource,
        starttime: Optional[datetime] = None,
        endtime: Optional[datetime] = None,
        min_peers=None,
        max_rows=None,
        include_first_hop=None,
        normalize_visibility=None,
    ):
        """
        Initialize and request Routing History.

        :param resource: The Autonomous System Number for which to return prefixes
        :param starttime: The start time for the query. (defaults to two weeks before
            current date and time)
        :param endtime: The start time for the query. (defaults to two weeks before
            current date and time)
        :param min_peers: Minimum number of full-feed RIS peers seeing the route
            for the segment to be included in the results. Excludes low-visibility/localized
            announcements. (default 10)
        :param_max_rows: The maximum number of routes to return. This is a soft limit:
            all recorded routes for each origin ASN are returned, but when the row limit is
            reached no more origins will be returned. (default: 3000)
        :pararm_include_first_hop: Include the first hop ASN in the route, instead of just
            the origin ASN. (default: false)
        :param_normalize_visibility: Add a visibility field to each timeline indicating the
            visibility of the route (according to RIS) at that point in time. The visibility is
            computed as the peers_seeing divided by the number of RIS full table peers
            at the time. (default: false)
        .. code-block:: python

            import prsw
            from datetime import datetime

            ripe = prsw.RIPEstat()

            start = datetime.fromisoformat("2021-01-01T12:00:00.000000")
            end = datetime.now()

            prefixes = ripe.routing_history(
                3333,                # Autonomous System Number
                starttime=start,     # datetime
                endtime=end,         # datetime
                min_peers=20         # int
                )

        """

        params = {
            "preferred_version": RoutingHistory.VERSION,
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
        if min_peers:
            if isinstance(min_peers, int):
                params["min_peers"] = str(min_peers)
            else:
                raise ValueError("min_peers expected to be int")
        if max_rows:
            if isinstance(max_rows, int):
                params["max_rows"] = str(max_rows)
            else:
                raise ValueError("max_rows expected to be int")
        if include_first_hop:
            if isinstance(include_first_hop, bool):
                params["include_first_hop"] = str(include_first_hop)
            else:
                raise ValueError("include_first_hop expected to be bool")
        if normalize_visibility:
            if isinstance(normalize_visibility, bool):
                params["normalize_visibility"] = str(include_first_hop)
            else:
                raise ValueError("include_first_hop expected to be a bool")

        self._api = RIPEstat._get(RoutingHistory.PATH, params)

    def __getitem__(self, index):
        """Get a specific index of the returned routing history."""
        return self.routing_history[index]

    def __iter__(self):
        """Provide a way to iterate over routing history."""
        return self.routing_history.__iter__()

    def __len__(self):
        """Get the number of origins in routing history."""
        return len(self.routing_history)

    @property
    def origin(self):
        """List of origins included in the response"""
        return [e["origin"] for e in self._api.data["by_origin"]]

    @property
    def routing_history(self):
        """
        A list of all entries in the history including their timeline

        Returns a **list** of `Origin` named tuples
        """

        Origin = namedtuple("Origin", ["origin", "prefixes"])
        PrefixHistory = namedtuple("PrefixHistory", ["prefix", "timelines"])
        Timeline = namedtuple("Timeline", ["starttime", "endtime"])

        result = []
        for origin in self._api.data["by_origin"]:
            prefixes = []
            for prefix in origin["prefixes"]:
                ip_network = ipaddress.ip_network(prefix["prefix"], strict=False)
                timelines = []

                for timeline in prefix["timelines"]:
                    starttime = datetime.fromisoformat(timeline["starttime"])
                    endtime = datetime.fromisoformat(timeline["endtime"])

                    timelines.append(Timeline(starttime=starttime, endtime=endtime))

                tuple_data = {"prefix": ip_network, "timelines": timelines}

                prefixes.append(PrefixHistory(**tuple_data))

            tuple_data = {"origin": origin["origin"], "prefixes": prefixes}

            result.append(Origin(**tuple_data))

        return result

    @property
    def latest_max_ff_peers(self):
        """This gives the number of maximum full-table peers seen as per IP version in RIS."""
        return self._api.data["latest_max_ff_peers"]

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
        try:
            return int(self._api.data["resource"])
        except ValueError:
            return self._api.data["resource"]
