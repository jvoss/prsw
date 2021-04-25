"""Provide the RIPEstat class."""

from functools import partial
from typing import Optional, Type

from .api import get
from .stat.abuse_contact_finder import AbuseContactFinder
from .stat.announced_prefixes import AnnouncedPrefixes
from .stat.asn_neighbours import ASNNeighbours
from .stat.looking_glass import LookingGlass
from .stat.network_info import NetworkInfo
from .stat.ris_peers import RISPeers
from .stat.rpki_validation_status import RPKIValidationStatus
from .stat.whats_my_ip import WhatsMyIp


class RIPEstat:
    """
    The RIPEstat class provides a convenient way to access the RIPEstat public API.

    Instances of this class are the gateway to interacting with RIPE's stat API
    through PRSW. **If you have a `sourceapp` parameter from RIPE, see `__init__`
    documentation for details.**

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()

    """

    def __init__(
        self, data_overload_limit: Optional[str] = "", sourceapp: Optional[str] = ""
    ) -> None:
        """
        Initialize a RIPEstat instance.

        :param data_overload_limit: Override the soft-limit check (
            see `data_overload_limit()`)
        :param sourceapp: A unique identifier attached to API calls. This identifier
            helps RIPE assit you when you encounter any problems with the system. The
            identifier can be your project name or your company's. See
            `RIPEstat API Overview <https://stat.ripe.net/docs/data_api/#Overview>`_
            for details.
        """
        self.sourceapp = sourceapp
        self.data_overload_limit = data_overload_limit

        return

    @property
    def data_overload_limit(self) -> str:
        """
        The data overload prevention is to protect users, especially widgets, from
        getting more data than they can handle. For this reason some data calls already
        support a soft-limit check which returns a warning if the output looks to be
        more than usual.

        This prevention mechanism should only kick in if the request stems from a
        browser (the referrer header set), but in case it happens for a non-browser
        request, it can easily suppressed by the "data_overload_limit" parameter set
        to "ignore".
        """
        return self._data_overload_limit

    @data_overload_limit.setter
    def data_overload_limit(self, string):
        if string == "ignore" or string == "":
            self._data_overload_limit = string
        else:
            raise ValueError("data_overload_limit expected 'ignore' or blank string")

    def _get(self, path, params=None):
        """Retrieve the requested path with parameters as GET from the API."""
        params = {} if params is None else params

        if self.data_overload_limit:
            params["data_overload_limit"] = "ignore"
        if self.sourceapp:
            params["sourceapp"] = self.sourceapp

        return get(path, params)

    @property
    def abuse_contact_finder(self) -> Type[AbuseContactFinder]:
        """Lazy alias to :class:`.stat.AbuseContactFinder`."""
        return partial(AbuseContactFinder, self)

    @property
    def announced_prefixes(self) -> Type[AnnouncedPrefixes]:
        """Lazy alias to :class:`.stat.AnnouncedPrefixes`."""
        return partial(AnnouncedPrefixes, self)

    @property
    def asn_neighbours(self) -> Type[ASNNeighbours]:
        """Lazy alias to :class:`.stat.ASNNeighbours`."""
        return partial(ASNNeighbours, self)

    @property
    def looking_glass(self) -> Type[LookingGlass]:
        """Lazy alias to :class:`.stat.LookingGlass`."""
        return partial(LookingGlass, self)

    @property
    def network_info(self) -> Type[NetworkInfo]:
        """Lazy alias to :class:`.stat.NetworkInfo`."""
        return partial(NetworkInfo, self)

    @property
    def ris_peers(self) -> Type[RISPeers]:
        """Lazy alias to :class:`.stat.RISPeers`."""
        return partial(RISPeers, self)

    @property
    def rpki_validation_status(self) -> Type[RPKIValidationStatus]:
        """Lazy alias to :class:`.stat.RPKIValidationStatus`."""
        return partial(RPKIValidationStatus, self)

    @property
    def whats_my_ip(self) -> Type[WhatsMyIp]:
        """Laze alias to :class:`.stat.WhatsMyIp`."""
        return partial(WhatsMyIp, self)
