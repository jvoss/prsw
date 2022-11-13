import pytest
from unittest import mock

from . import UnitTest

from prsw import RIPEstat
from prsw.stat.abuse_contact_finder import AbuseContactFinder
from prsw.stat.announced_prefixes import AnnouncedPrefixes
from prsw.stat.asn_neighbours import ASNNeighbours
from prsw.stat.looking_glass import LookingGlass
from prsw.stat.network_info import NetworkInfo
from prsw.stat.ris_peers import RISPeers
from prsw.stat.routing_history import RoutingHistory
from prsw.stat.rpki_validation_status import RPKIValidationStatus
from prsw.stat.whats_my_ip import WhatsMyIp


class TestRIPEstat(UnitTest):
    def mocked_get(*args):
        """Mock prsw.api.get()"""

        class MockOutputResponse:
            def __init__(self, path, params):
                self.path = path
                self.params = params

        return MockOutputResponse(*args)

    def test__init__no_params(self):
        ripestat = RIPEstat()
        assert isinstance(ripestat, RIPEstat)

    def test__init__sourceapp(self):
        name = "testapp"
        ripestat = RIPEstat(sourceapp=name)
        assert ripestat.sourceapp is name

    def test__init__data_overload_limit(self):
        limit = "ignore"
        ripestat = RIPEstat(data_overload_limit=limit)
        assert ripestat.data_overload_limit is limit

    def test__init__invalid_data_overload_limit(self):
        with pytest.raises(ValueError):
            RIPEstat(data_overload_limit="invalid-parameter")

    @mock.patch("prsw.ripe_stat.get", side_effect=mocked_get)
    def test__get_with_sourceapp(self, mock_get):
        app = "under-test"
        ripestat = RIPEstat(sourceapp=app)

        ripestat._get("/test")

        mock_get.assert_called()
        mock_get.assert_called_with("/test", {"sourceapp": app})

    @mock.patch("prsw.ripe_stat.get", side_effect=mocked_get)
    def test__get_with_data_overload_limit(self, mock_get):
        ripestat = RIPEstat(data_overload_limit="ignore")
        ripestat._get("/test")

        mock_get.assert_called_with("/test", {"data_overload_limit": "ignore"})

    def test_abuse_contact_finder(self):
        assert self.ripestat.abuse_contact_finder.func == AbuseContactFinder

    def test_announced_prefixes(self):
        assert self.ripestat.announced_prefixes.func == AnnouncedPrefixes
        
    def test_routing_history(self):
        assert self.ripestat.routing_history.func == RoutingHistory

    def test_asn_neighbours(self):
        assert self.ripestat.asn_neighbours.func == ASNNeighbours

    def test_looking_glass(self):
        assert self.ripestat.looking_glass.func == LookingGlass

    def test_network_info(self):
        assert self.ripestat.network_info.func == NetworkInfo

    def test_ris_peers(self):
        assert self.ripestat.ris_peers.func == RISPeers

    def test_rpki_validation_status(self):
        assert self.ripestat.rpki_validation_status.func == RPKIValidationStatus

    def test_whats_my_ip(self):
        assert self.ripestat.whats_my_ip.func == WhatsMyIp
