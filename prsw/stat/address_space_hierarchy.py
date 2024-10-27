"""Provides the Address Space Hierarchy endpoint."""
from collections import namedtuple

import ipaddress
from datetime import datetime

from prsw.validators import Validators


class AddressSpaceHierarchy:
    """
    This data call returns address space objects (inetnum or inet6num)
    from the RIPE Database related to the queried resource.
    Less- and more-specific results are first-level only, further levels
    would have to be retrieved iteratively.

    Reference: `<https://stat.ripe.net/docs/data_api#address-space-hierarchy>`

    ========================== ===============================================================
    Property                   Description
    ========================== ===============================================================
    ``resource``               The ASN this query is based on.
    ``exact_inetnums``         A list containing exact matches for the queried resource
    ``more_specific_inetnums`` A list containing first level more specific blocks underneath the queried resource. Some of these may be aggregated according to the 'aggr_levels_below' query parameter.
    ``less_specific``          A list containing first level less specific (parent) blocks above the queried resource.
    ``rir``                    Name of the RIR where the results are from.
    ``query_time``             Holds the time the query was based on
    ========================== ===============================================================

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()
        result = ripe.address_space_hierarchy('193.0.0.0/21')

        print(result)
    """

    PATH = "/address-space-hierarchy"
    VERSION = "1.3"

    def __init__(self, RIPEstat, resource):
        """
        Initialize and request AddressSpaceHierarchy.

        :param resource: The prefix or IP range the address space hierarchy should be returned for.

        """

        if Validators._validate_ip_network(resource):
            resource = ipaddress.ip_network(resource, strict=False)
        else:
            raise ValueError("prefix must be valid IP network")

        params = {
            "preferred_version": AddressSpaceHierarchy.VERSION,
            "resource": str(resource)
        }

        self._api = RIPEstat._get(AddressSpaceHierarchy.PATH, params)

    @property
    def resource(self):
        """The prefix this query is based on."""
        return ipaddress.ip_network(self._api.data["resource"])

    @property
    def exact_inetnums(self):
        """
        Returns a list containing exact matches for the queried resource

        .. code-block:: python

            import prsw

            ripe = prsw.RIPEstat()
            result = ripe.address_space_hierarchy('193.0.0.0/21')

            for inetnum in result.exact_inetnums:
                print(inetnum)

        """
        return self._api.data["exact"]

    @property
    def more_specific_inetnums(self):
        """
        Returns a list containing first level more specific blocks underneath
        the queried resource. Some of these may be aggregated according to
        the 'aggr_levels_below' query parameter.

        .. code-block:: python

            finder = ripe.address_space_hierarchy('193.0.0.0/21')

            for inetnum in finder.more_specific_inetnums:
                print(inetnum)

        """
        return self._api.data["more_specific"]

    @property
    def less_specific_inetnums(self):
        """
        Returns a list containing first level less specific (parent) blocks 
        above the queried resource.

        .. code-block:: python

            finder = ripe.address_space_hierarchy('193.0.0.0/21')

            for inetnum in finder.less_specific_inetnums:
                print(inetnum)

        """
        return self._api.data["less_specific"]

    @property
    def rir(self):
        """Name of the RIR where the results are from."""
        return self._api.data["rir"]

    @property
    def query_time(self):
        """**datetime** of used by query."""
        return datetime.fromisoformat(
            self._api.data["query_time"]
        )

