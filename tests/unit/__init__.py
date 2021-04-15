"""RSAW Unit test suite."""
from rsaw import RIPEstat


class UnitTest:
    """Base class for RSAW unit tests."""

    def setup(self):
        """Setup runs before all test cases."""
        self.ripestat = RIPEstat(sourceapp="dummy-test")
