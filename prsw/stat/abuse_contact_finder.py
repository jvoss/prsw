"""Provides the Abuse Contact Finder endpoint."""

import ipaddress

from datetime import datetime

from prsw.validators import Validators


class AbuseContactFinder:
    """
    The main purpose of this data call is to return abuse contact informations for a
    Internet number resource.

    .. note::
        Note that this information is in many cases incorrect or
        not available.

    Reference: `<https://stat.ripe.net/docs/data_api#abuse-contact-finder>`_

    ======================= ===========================================================
    Property                Description
    ======================= ===========================================================
    ``abuse_contacts``      list of dedicated abuse contacts (email addresses)
    ``authoritative_rir``   Regional Internet Registry authoritative for the looked up resource
    ``earliest_time``       Holds the time the query was based on.
    ``latest_time``         Holds the time the query was based on.
    ``resource``            The resource the query was based on.
    ======================= ===========================================================

    .. code-block:: python

        import prsw

        ripe = prsw.RIPEstat()

        # Lookup by ASN
        contacts = ripe.abuse_contact_finder(3333)

        # Lookup by IPv4 or IPv6 Address
        contacts = ripe.abuse_contact_finder(IPv4Address('193.0.0.0'))

        # Lookup by IPv4 or IPv6 Network (prefix)
        contacts = ripe.abuse_contact_finder(IPv4Network('193.0.0.0/23))

        # See each property below for additional details on each of the returned
        # properties listed in the table above.

        contacts.resource
        # resource used in query:
        # 3333 -or- IPv4Address('193.0.0.0') -or- IPv4Network('193.0.0.0/23')

        contacts.earliest_time
        # datetime.datetime(2021, 4, 14, 12, 54, 37)

    """

    PATH = "/abuse-contact-finder"
    VERSION = "2.1"

    def __init__(self, RIPEstat, resource):
        """
        Initialize and request Abuse Contacts.

        :param resource: A prefix, single IP address or ASN

        .. code-block:: python

            contacts = ripe.abuse_contact_finder('193.0.0.0')

        """

        params = {"preferred_version": AbuseContactFinder.VERSION}

        params["resource"] = str(self._resource(resource))

        self._api = RIPEstat._get(AbuseContactFinder.PATH, params)

    def _resource(self, value):
        """Validate and return a valid resource value."""
        resource = None

        # first check if resource is an ASN
        if Validators._validate_asn(str(value)):
            resource = int(value)
        # next check if resource is an IP address)
        elif Validators._validate_ip_address(value):
            resource = ipaddress.ip_address(value)
        # last check if resource is an IP network
        elif Validators._validate_ip_network(value):
            resource = ipaddress.ip_network(value)
        else:
            raise ValueError("Expected ASN int or valid IP address or network")

        return resource

    @property
    def abuse_contacts(self):
        """
        Returns a list of dedicated abuse contacts (email addresses)

        .. code-block:: python

            finder = ripe.abuse_contact_finder(3333)

            for email_address in finder.abuse_contacts:
                print(email_address)

        """
        return self._api.data["abuse_contacts"]

    @property
    def authoritative_rir(self):
        """
        Returns the Regional Internet Registry authoritative for the looked up resource

        .. code-block:: python

            contacts = ripe.authoritative_rir('193.0.0.0')

            contacts.authorities
            # 'ripe'

        """
        return self._api.data["authoritative_rir"]

    @property
    def earliest_time(self):
        """Holds the time the query was based on."""
        return datetime.fromisoformat(self._api.data["earliest_time"])

    @property
    def latest_time(self):
        """Holds the time the query was based on."""
        return datetime.fromisoformat(self._api.data["latest_time"])

    @property
    def resource(self):
        """Holds the resource the query was based on."""
        return self._resource(self._api.data["parameters"]["resource"])
