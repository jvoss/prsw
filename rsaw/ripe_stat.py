from functools import partial
from typing import Optional, Type

from ._api import get as get

from .api.announced_prefixes import AnnouncedPrefixes
from .api.looking_glass import LookingGlass as looking_glass
from .api.rpki_validation_status import RPKIValidationStatus as rpki_validation_status


class RIPEstat:
    def __init__(
        self, data_overload_limit: Optional[str] = "", sourceapp: Optional[str] = ""
    ) -> None:
        self.sourceapp = sourceapp
        self.data_overload_limit = data_overload_limit

        return

    @property
    def data_overload_limit(self) -> str:
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
            params += f"&data_overload_limit=ignore"
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
