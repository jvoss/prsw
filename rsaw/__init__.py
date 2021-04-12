"""
RIPEStat API Wrapper.

RSAW, the RIPEStat API Wrapper, is a python package that allows for 
pythonic interaction with the RIPEStat public API.

More RIPEStat API information is available at:
https://stat.ripe.net/docs/data_api

"""

from .announced_prefixes import AnnouncedPrefixes as announced_prefixes
from .looking_glass import LookingGlass as looking_glass
from .rpki_validation_status import RPKIValidationStatus as rpki_validation_status

__version__ = "0.0.1"
