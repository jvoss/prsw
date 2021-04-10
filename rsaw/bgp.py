import ipaddress

from .api import get
from datetime import datetime
from typing import Optional


class AnnouncedPrefixes:
    """
    This data call returns all announced prefixes for a given ASN. The results
    can be restricted to a specific time period.

    Reference: `<https://stat.ripe.net/docs/data_api#announced-prefixes>`_

    .. code-block:: python

        import rsaw

        prefixes = rsaw.announced_prefixes(3333)

        for prefix in prefixes:
            print(prefix)

    """

    PATH = "/announced-prefixes/"

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

        params = "resource=" + str(resource)

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
            for prefix in prefixes:
                print(prefix['prefix'], prefix['timelines'])

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
        """Earliest `datetime` a prefix was observed."""
        return datetime.fromisoformat(self._api.data["earliest_time"])

    def latest_time(self):
        """Latest `datetime` a prefix was observed."""
        return datetime.fromisoformat(self._api.data["latest_time"])

    def prefixes(self):
        """
        A list of all announced prefixes + the timelines when they were visible.
        """
        prefixes = []

        for prefix in self._api.data["prefixes"]:
            ip_network = ipaddress.ip_network(prefix["prefix"], strict=False)
            timelines = []

            for timeline in prefix["timelines"]:
                for key, time in timeline.items():
                    timelines.append({key: datetime.fromisoformat(time)})

            prefixes.append({"prefix": ip_network, "timelines": timelines})

        return prefixes

    def query_endtime(self):
        """The `datetime` at which the query ended."""
        return datetime.fromisoformat(self._api.data["query_endtime"])

    def query_starttime(self):
        """The `datetime` at which the query started."""
        return datetime.fromisoformat(self._api.data["query_starttime"])

    def resource(self):
        """The resource queried."""
        return self._api.data["resource"]


class RPKIValidationStatus:
    """
    This data call returns the RPKI validity state for a combination of prefix
    and Autonomous System. This combination will be used to perform the lookup
    against the RIPE NCC's RPKI Validator, and then return its RPKI validity
    state.

    Arguments:
        resource {str} -- The ASN used to perform the RPKI validity state lookup.
        prefix {str}   -- The prefix to perform the RPKI validity state lookup. Note
                        the prefix's length is also taken from this field.

    Returns:
        RPKIValidationStatus {obj} --
    """

    PATH = "/rpki-validation/"

    def __init__(
        self,
        resource,
        prefix: ipaddress,
    ):
        # validate prefix)
        ipaddress.ip_network(prefix, strict=False)

        params = "resource=" + str(resource) + "&prefix=" + str(prefix)
        self._api = get(RPKIValidationStatus.PATH, params)

    def prefix(self):
        """
        The prefix this query is based on.
        """
        return ipaddress.ip_network(self._api.data["prefix"], strict=False)

    def resource(self):
        """
        The resource (ASN) this query is based on.
        """
        return self._api.data["resource"]

    def status(self):
        """
        The RPKI validity state, according to RIPE NCC's RPKI validator. Possible
        states are:

        Returns:
            "valid"             - the announcement matches a roa and is valid

            "invalid_asn"       - there is a roa with the same (or covering)
                                  prefix, but a different ASN

            "invalid_length"    - the announcement's prefix length is greater
                                  than the ROA's maximum length

            "unknown"           - no ROA found for the announcement
        """
        return self._api.data["status"]

    def validating_roas(self):
        roas = []

        for roa in self._api.data["validating_roas"]:
            r_dict = {}

            # repack API response with ipaddress object
            for k, v in roa.items():
                if k == "prefix":
                    v = ipaddress.ip_network(roa["prefix"], strict=False)

                r_dict[k] = v

            roas.append(r_dict)

        return roas
