import ipaddress

from collections import namedtuple
from datetime import datetime
from typing import Optional

from .api import get


class AnnouncedPrefixes:
    """
    This data call returns all announced prefixes for a given ASN. The results
    can be restricted to a specific time period.

    Reference: `<https://stat.ripe.net/docs/data_api#announced-prefixes>`_

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
        resource,
        starttime: Optional[datetime] = None,
        endtime: Optional[datetime] = None,
        min_peers_seeing=None,
    ):
        """Initialize and request Announced Prefixes.

        :param resource: The Autonomous System Number for which to return prefixes
        :param starttime: The start time for the query. (defaults to two
            weeks before current date and time)
        :param endtime: The end time for the query. (defaults to now)
        :param min_peers_seeing: Minimum number of RIS peers seeing the prefix for
            it to be included in the results. Excludes low
            visibility/localized announcements. (default 10)
        """

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

        self._api = get(AnnouncedPrefixes.PATH, params)

    def __iter__(self):
        """Provide a way to iterate over announced prefixes.

        Example:

        .. code-block:: python

            prefixes = rsaw.announced_prefixes(3333)
            for announced_prefix in prefixes:
                print(announced_prefix.prefix, announced_prefix.timelines)

        """

        for prefix in self.prefixes():
            yield prefix

    def __getitem__(self, index):
        return self.prefixes()[index]

    def __len__(self):
        """Get the number of prefixes in announced prefixes

        Example:

        .. code-block:: python

            prefixes = rsaw.announced_prefixes(3333)
            print(len(prefixes))

        """
        return len(self.prefixes())

    def earliest_time(self):
        """Earliest `datetime` data is available for."""
        return datetime.fromisoformat(self._api.data["earliest_time"])

    def latest_time(self):
        """Latest `datetime` data is available for."""
        return datetime.fromisoformat(self._api.data["latest_time"])

    def prefixes(self):
        """
        A list of all announced prefixes + the timelines when they were visible.
        """
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

    def query_endtime(self):
        """The `datetime` at which the query ended."""
        return datetime.fromisoformat(self._api.data["query_endtime"])

    def query_starttime(self):
        """The `datetime` at which the query started."""
        return datetime.fromisoformat(self._api.data["query_starttime"])

    def resource(self):
        """The resource used for the query."""
        return self._api.data["resource"]


class RPKIValidationStatus:
    """
    This data call returns the RPKI validity state for a combination of prefix
    and Autonomous System. This combination will be used to perform the lookup
    against the RIPE NCC's RPKI Validator, and then return its RPKI validity
    state.

    Reference: `<https://stat.ripe.net/docs/data_api#rpki-validation>`_

    .. code-block:: python

        import rsaw

        result = rsaw.rpki_validation_status(3333, '193.0.0.0/21')
        print(result.status)

        for roa in result.validating_roas():
            print(roa.origin, roa.prefix, roa.validity, roa.source)
    """

    PATH = "/rpki-validation/"
    VERSION = "0.2"

    def __init__(
        self,
        resource,
        prefix: ipaddress.ip_network,
    ):
        """Initialize and request RPKIValidationStatus

        :param resource: The ASN used to perform the RPKI validity state lookup.
        :param prefix: The prefix to perform the RPKI validity state lookup.
            Note the prefix's length is also taken from this field.
        """

        # validate and sanitize prefix (ensure is proper boundary)
        prefix = ipaddress.ip_network(prefix, strict=False)

        params = f"preferred_version={RPKIValidationStatus.VERSION}&"
        params += "resource=" + str(resource) + "&prefix=" + str(prefix)

        self._api = get(RPKIValidationStatus.PATH, params)

    def prefix(self):
        """The prefix this query is based on."""
        return ipaddress.ip_network(self._api.data["prefix"], strict=False)

    def resource(self):
        """The resource (ASN) this query is based on."""
        return self._api.data["resource"]

    def status(self):
        """
        The RPKI validity state, according to RIPE NCC's RPKI validator. Possible
        states are:

        `"valid"` the announcement matches a roa and is valid

        `"invalid_asn"` there is a roa with the same (or covering)
        prefix, but a different ASN

        `"invalid_length"` the announcement's prefix length is greater
        than the ROA's maximum length

        `"unknown"` no ROA found for the announcement
        """
        return self._api.data["status"]

    def validating_roas(self):
        """A list of validating ROAs"""
        roas = []
        ROA = namedtuple(
            "ROA", ["origin", "prefix", "validity", "source", "max_length"]
        )

        for roa in self._api.data["validating_roas"]:
            roa_dict = {}

            # repack API response with ipaddress object
            for k, v in roa.items():
                if k == "prefix":
                    v = ipaddress.ip_network(roa["prefix"], strict=False)

                roa_dict[k] = v

            roas.append(ROA(**roa_dict))
            # roas.append(r_dict)

        return roas
