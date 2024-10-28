"""PRSW Unit test suite."""

from prsw import RIPEstat


class UnitTest:
    """Base class for PRSW unit tests."""

    def setup_method(self):
        """Setup runs before all test cases."""
        self.ripestat = RIPEstat(sourceapp="dummy-test")
