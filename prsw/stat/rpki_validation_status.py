"""Provides the RPKI Validation Status endpoint."""

import ipaddress

from collections import namedtuple

from prsw.validators import Validators


class RPKIValidationStatus:
    """
    This data call returns the RPKI validity state for a combination of prefix
    and Autonomous System. This combination will be used to perform the lookup
    against the RIPE NCC's RPKI Validator, and then return its RPKI validity
    state.

    Reference: `<https://stat.ripe.net/docs/data_api#rpki-validation>`_

    =================== ===============================================================
    Property            Description
    =================== ===============================================================
    ``prefix``          The prefix this query is based on
    ``resource``        The ASN this query is based on.
    ``status``          The RPKI validity state, according to RIPE NCC's RPKI validator
    ``validating_roas`` A list if validating ROAs
    =================== ===============================================================

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()
        result = ripe.rpki_validation_status(3333, '193.0.0.0/21')

        print(result.status)

        for roa in result.validating_roas:
            # ROA(
            #   origin=3333,
            #   prefix=IPv4Network('193.0.0.0/21'),
            #   validity='valid',
            #   source='RIPE NCC RPKI Root',
            #   max_length=21
            # )

            print(roa.origin, roa.prefix, roa.validity, roa.source)
    """

    PATH = "/rpki-validation"
    VERSION = "0.2"

    def __init__(
        self,
        RIPEstat,
        resource,
        prefix: ipaddress.ip_network,
    ):
        """
        Initialize and request RPKIValidationStatus.

        :param resource: The ASN used to perform the RPKI validity state lookup.
        :param prefix: The prefix to perform the RPKI validity state lookup. Note the
            prefix’s length is also taken from this field.

        """

        # validate and sanitize prefix (ensure is proper boundary)
        if Validators._validate_ip_network(prefix):
            prefix = ipaddress.ip_network(prefix, strict=False)
        else:
            raise ValueError("prefix must be valid IP network")

        params = {
            "preferred_version": RPKIValidationStatus.VERSION,
            "resource": str(resource),
            "prefix": str(prefix),
        }

        self._api = RIPEstat._get(RPKIValidationStatus.PATH, params)

    @property
    def prefix(self):
        """The prefix this query is based on."""
        return ipaddress.ip_network(self._api.data["prefix"], strict=False)

    @property
    def resource(self):
        """The ASN this query is based on."""
        return int(self._api.data["resource"])

    @property
    def status(self):
        """
        The RPKI validity state, according to RIPE NCC's RPKI validator. Possible
        states are:

        * ``"valid"`` the announcement matches a roa and is valid

        * ``"invalid_asn"`` there is a roa with the same (or covering)
          prefix, but a different ASN

        * ``"invalid_length"`` the announcement's prefix length is greater
          than the ROA's maximum length

        * ``"unknown"`` no ROA found for the announcement
        """
        return self._api.data["status"]

    @property
    def validating_roas(self):
        """
        A list of validating ROAs.

        Returns a **list** of `ROA` named tuples with the following properties:

        ==============   ====================================================
        Property         Description
        ==============   ====================================================
        ``origin``       **Int** representing the AS
        ``prefix``       **IPv4Network** or **IPv6Network** of the ROA record
        ``source``       Source of the ROA
        ``max_length``   Maximum permitted prefix length **int**
        ==============   ====================================================

        """
        roas = []
        ROA = namedtuple(
            "ROA", ["origin", "prefix", "validity", "source", "max_length"]
        )

        for roa in self._api.data["validating_roas"]:
            roa_dict = {}

            # repack API response with ipaddress object
            for k, v in roa.items():
                if k == "origin":
                    v = int(v)
                if k == "prefix":
                    v = ipaddress.ip_network(roa["prefix"], strict=False)

                roa_dict[k] = v

            roas.append(ROA(**roa_dict))

        return roas
