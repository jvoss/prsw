"""Provides the ASN Neighbours endpoint."""

from collections import namedtuple
from datetime import datetime
from typing import Optional

from prsw.validators import Validators


class ASNNeighbours:
    """
    This data call shows information on the network neighbours for a given ASN. This
    includes statistical information, the list of observed ASN neighbours and,
    depending on the level of detail, the ASN paths that this data is based on.

    Reference: `<https://stat.ripe.net/docs/data_api#asn-neighbours>`_

    =================== ===============================================================
    Property            Description
    =================== ===============================================================
    ``query_time``      Reflects the time the data is valid for.
    ``neighbours``      Contains all neighbours that were seen at the defined point in
                        time (see ``neighbours()``)
    ``neighbor_counts`` Shows total counts for the neighbours (see
                        ``neighbour_counts()``)
    ``resource``        Defines the resource used for the query.
    ``lod``             Level of detail.
    ``latest_time``     Latest time in dataset.
    ``earliest_time``   Earliest time in dataset.
    =================== ===============================================================

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()
        neighbours = ripe.asn_neighbours(3333, lod=1)

        neighbours.query_time
        # datetime.datetime(2021, 3, 31, 8, 0)

        for neighbour in neighbours:
            neighbour
            # ASNNeighbour(
            #   asn: 1853,
            #   position: "left",
            #   details: {
            #       "peer_count": { "v4": 288, "v6": 0 },
            #       "path_count": 81,
            #       "paths": [
            #           ASNNeighbourPath(
            #               path: (1103, 20965, 1853, 1205)
            #               locations: {
            #                   "v4": [
            #                       {
            #                           "location": "rrc03",
            #                           "peer_count": 3
            #                       },
            #                   ],
            #                   "v6": [
            #                       {
            #                           "location": "rrc03",
            #                           "peer_count": 3
            #                       },
            #                   ]
            #               }
            #           )
            #       ]
            #   }
            # )

        neighbours.neighbour_counts
        # ASNNeighbourCount(left=1, right=0, uncertain=1, unique=2)

        neighbours.resource
        # 3333

        neighbours.lod
        # 1

        neighbours.latest_time
        # datetime.datetime(2021, 3, 31, 8, 0)

        neighbours.earliest_time
        # datetime.datetime(2021, 3, 31, 8, 0)

    """

    PATH = "/asn-neighbours"
    VERSION = "4.1"

    def __init__(
        self,
        RIPEstat,
        resource,
        lod: Optional[int] = 0,
        query_time: Optional[datetime] = None,
    ):
        """
        Initialize and request ASN Neighbors.

        :param resource: The ASN for this query.
        :param lod: 0 or 1, defines how main details are returned in the result
        :param query_time: Query time for the query. Default is the latest available
            data point.

        .. code-block:: python

            import prsw
            from datetime import datetime

            timestamp = datetime.now()

            neighbours = ripe.asn_neighbours(3333, lod=1, query_time=timestamp)

        """

        params = {"preferred_version": ASNNeighbours.VERSION, "resource": str(resource)}

        if Validators._validate_asn(resource):
            pass
        else:
            raise ValueError("resource must be int between 0 and 4294967295")

        if int(lod) == 0 or int(lod) == 1:
            params["lod"] = str(lod)
        else:
            raise ValueError("lod must be 0 or 1")

        if query_time:
            if Validators._validate_datetime(query_time):
                params["query_time"] = query_time.isoformat()
            else:
                raise ValueError("query_time expected to be datetime")

        self._api = RIPEstat._get(ASNNeighbours.PATH, params)
        self._neighbours = self._objectify_neighbors(self._api.data["neighbours"])

    def __iter__(self):
        """
        Provide a way to iterate over neighbours.

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            neighbours = ripe.asn_neighbours(3333)

            for neighbour in neighbours:
                print(neighbour.asn, neighbour.position)

        """
        return self.neighbours.__iter__()

    def __len__(self):
        """
        Get the number of neighbours in the response.

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            neighbours = ripe.asn_neighbours(3333)

            print(len(neighbours))

        """
        return len(self.neighbours)

    def _objectify_neighbors(self, api_neighbors):
        """Process paths in neighbours details..."""

        neighbours = []
        ASNNeighbour = namedtuple("ASNNeighbour", ["asn", "position", "details"])
        ASNNeighbourPath = namedtuple("ASNNeighbourPath", ["path", "locations"])

        for neighbour in api_neighbors:
            paths = []

            if "details" in neighbour:  # only present when lod=1
                for path in neighbour["details"]["paths"]:
                    # path gets mutated on first run (subsequent runs are unnecessary)
                    if path.__class__.__name__ != "ASNNeighbourPath":
                        as_path = tuple(map(int, path["path"].split(" ")))
                        locations = path["locations"]
                        paths.append(
                            ASNNeighbourPath(path=as_path, locations=locations)
                        )

                neighbour["details"]["paths"] = paths
            else:
                neighbour["details"] = None

            neighbours.append(ASNNeighbour(**neighbour))

        return neighbours

    @property
    def earliest_time(self):
        """Earliest **datetime** data is available for."""
        return datetime.fromisoformat(self._api.data["earliest_time"])

    @property
    def latest_time(self):
        """Latest **datetime** data is available for."""
        return datetime.fromisoformat(self._api.data["latest_time"])

    @property
    def lod(self):
        """Level of detail. See ``neighbors()``"""
        return int(self._api.data["lod"])

    @property
    def neighbours(self):
        """
        Contains all neighbours that were seen at the defined point in time.

        Details are only returned if the level of detail ("lod") is 1:

        ==============  =============================================================
        Attribute       Description
        ==============  =============================================================
        ``peer_count``  Summarizes the number of peers seeing this neighbour/position
                        combination.
        ``path_count``  States in how many paths this neighbour/position combination
                        has been seen.
        ``paths``       Contains details about the paths, including the RRC location
                        where it has been seen and by how many (full-table) peers.
        ==============  =============================================================

        """
        return self._neighbours

    @property
    def neighbour_counts(self):
        """
        Shows total counts for the neighbours.

        The total number of "left", "right" and "unique" neighbours found. Neighbours
        that have been seen as left neighbours, but only as direct peers of one of our
        route collectors (RIS collectors), are flagged "uncertain" because our own
        peering with this ASN could artifically include it as neigbour. ASNs that have
        been seen as a left neighbour and not as a direct peer with RIS are not flagged
        as "uncertain".

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            neighbours = ripe.asn_neighbours(3333)

            neighbours.neighbour_counts
            # ASNNeighbourCount(left=1, right=0,uncertain=1,unique=2)

        """
        ASNNeighbourCount = namedtuple(
            "ASNNeighbourCount", ["left", "right", "uncertain", "unique"]
        )

        params = {}

        for k, v in self._api.data["neighbour_counts"].items():
            params[k] = int(v)  # repack counts as integers

        return ASNNeighbourCount(**params)

    @property
    def query_time(self):
        """The **datetime** of the query."""
        return datetime.fromisoformat(self._api.data["query_time"])

    @property
    def resource(self):
        """The resource, autonomous system number, used for the query."""
        return int(self._api.data["resource"])
