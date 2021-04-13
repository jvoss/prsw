"""Provide the RIPEstat class."""

from functools import partial
from typing import Optional, Type

from ._api import get as get

from .stat.announced_prefixes import AnnouncedPrefixes
from .stat.looking_glass import LookingGlass as looking_glass
from .stat.rpki_validation_status import RPKIValidationStatus as rpki_validation_status


class RIPEstat:
    """
    The RIPEstat class provides a convenient way to access the RIPEstat public API.

    Instances of this class are the gateway to interacting with RIPE's stat API
    through RSAW. **If you have a `sourceapp` parameter from RIPE, see `__init__`
    documentation for details.**

    .. code-block:: python

        import rsaw

        ripe = rsaw.RIPEstat()

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

    def _get(self, path, params):
        """Retrieve the requested path with parameters as GET from the API."""
        if self.data_overload_limit:
            params += "&data_overload_limit=ignore"
        if self.sourceapp:
            params += f"&sourceapp={self.sourceapp}"

        return get(path, params)

    @property
    def announced_prefixes(self) -> Type[AnnouncedPrefixes]:
        """Lazy alias to :class:`.api.AnnouncedPrefixes`."""
        return partial(AnnouncedPrefixes, self)

    @property
    def looking_glass(self) -> Type[looking_glass]:
        """Lazy alias to :class:`.api.LookingGlass`."""
        return partial(looking_glass, self)

    @property
    def rpki_validation_status(self) -> Type[rpki_validation_status]:
        """Lazy alias to :class:`.api.RPKIValidationStatus`."""
        return partial(rpki_validation_status, self)
