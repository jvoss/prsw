"""Provides the Abuse Contact Finder endpoint."""

import ipaddress

from collections import namedtuple
from datetime import datetime

from prsw.validators import Validators


class AbuseContactFinder:
    """
    The main purpose of this data call is to return abuse contact informations for a
    Internet number resource.

    .. note::
        Note that this information is in many cases incorrect or
        not available.

    Additional information:
        * the resources RIR name (if available)
        * whether the queries resource is related to a special purpose Internet number
          resource (if available)
        * blocklist informations (if available)
        * additional information about the matchin autnum or inet(6)num object in the
          RIPE DB (e.g. holder name)
        * less and more specific IP prefixes/ranges for IP based queries

    Reference: `<https://stat.ripe.net/docs/data_api#abuse-contact-finder>`_

    ======================= ===========================================================
    Property                Description
    ======================= ===========================================================
    ``authorties``          List all RIRs that are responsible for the queried resource
    ``blocklist_info``      Lists the total amount of entries in one blocklist source
                            Every blocklist is given with the name as "list" and the
                            number of entries in the field "entries".
    ``global_network_info`` This contains information that are related to special
                            purpose Internet number resources, e.g. private address
                            space.
    ``anti_abuse_contacts`` Contains the anti-abuse contact informations (if available)
    ``holder_info``         Contains information found in the matching autnum or
                            inet(6)num object in the RIPE DB.
    ``less_specific``       Lists less specific IP prefixes/ranges found for the given
                            input resource.
    ``more_specific``       Lists more specific IP prefixes/ranges found for the given
                            input resource.
    ``resource``            The resource the query was based on.
    ``query_time``          Holds the time the query was based on.
    ======================= ===========================================================

    .. code-block:: python

        import prsw

        ripe = RIPEstat()

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

        contacts.query_time
        # datetime.datetime(2021, 4, 14, 12, 54, 37)

    """

    PATH = "/abuse-contact-finder"
    VERSION = "1.2"

    def __init__(self, RIPEstat, resource):
        """
        Initialize and request Absute Contacts.

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
    def anti_abuse_contacts(self):
        """
        This object contains anti-abuse contact information (if available)

        ========================    ===================================================
        Property                    Description
        ========================    ===================================================
        ``abuse_c``                 Dedicated abuse contact that is according to
                                    ripe-563, for further details refer to
                                    `This RIPE Labs article <https://labs.ripe.net/Members/kranjbar/implementation-details-of-policy-2011-06>`_.
                                    **If the abuse-c contact is available other contact
                                    fields (e.g. "extracted_mails") will be left
                                    empty.**
        ``emails``                  Any found email address is stated with a
                                    "description" and a "email" field
        ``extracted_emails``        Those contacts have been extracted/parsed from a
                                    RIPE DB object, the exact reference is given by
                                    "object-type" and "object-key".
        ``objects_with_remarks``    Any object that was found to contain anti-abuse
                                    related information is listed with a "type" field
                                    and a link to the RIPE DB web interface.
        ========================    ===================================================

        .. code-block:: python

            finder = ripe.abuse_contact_finder(3333)

            contacts = finder.anti_abuse_contacts
            # AntiAbuseContacts(
            #   abuse_c=[],
            #   email=[],
            #   extracted_emails=[],
            #   objects_with_remarks=[]
            # )

            for contact in contacts.abuse_c:
                print(contact["description"])
                print(contact["email"])
                print(contact["key"])

        """
        AntiAbuseContacts = namedtuple(
            "AntiAbuseContact",
            ["abuse_c", "emails", "extracted_emails", "objects_with_remarks"],
        )

        return AntiAbuseContacts(**self._api.data["anti_abuse_contacts"])

    @property
    def authorities(self):
        """
        List of all RIRs that are responsible for the queried resource.

        .. code-block:: python

            contacts = ripe.abuse_contact_finder('193.0.0.0')

            contacts.authorities
            # ['ripe']

        """
        return self._api.data["authorities"]

    @property
    def blocklist_info(self):
        """
        List of total amount of entries in one blocklist source. Every blocklist is
        given with the name as "list" and the number of entries in the field "entries".
        """
        return self._api.data["blocklist_info"]

    @property
    def global_network_info(self):
        """
        This contains information that are related to special purpose Internet number
        resources, e.g. private address space.

        .. code-block:: python

            contacts = ripe.abuse_contact_finder('192.0.0.0')

            contacts.global_network_info
            # GlobalNetworkInfo(description="", name="RIPE NCC PI Allocation")

            contacts.global_network_info.name
            # "RIPE NCC PI Allocation"

        """
        GlobalNetworkInfo = namedtuple(
            "GlobalNetworkInfo", ["description", "name", "source", "source_url"]
        )
        return GlobalNetworkInfo(**self._api.data["global_network_info"])

    @property
    def holder_info(self):
        """
        This contains information found in the matching autnum or inet(6)num object
        in the RIPE DB.

        ============    ===============================================================
        Property        Description
        ============    ===============================================================
        ``name``        "netname" for IP based queries, "as-name" for ASN based queries
        ``resource``    The resource that is mapped to the object (that doesn't have to
                        be the same as the given input)
        ============    ===============================================================

        .. code-block:: python

            contacts = ripe.abuse_contact_finder(3333)

            contacts.holder_info
            # HolderInfo(name=str, resource=str)

            print(contacts.holder_info.name)
            # "RIPE-NCC"

            print(contacts.holder_info.resource)
            # "3333"

        """
        HolderInfo = namedtuple("HolderInfo", ["name", "resource"])
        return HolderInfo(**self._api.data["holder_info"])

    @property
    def less_specifics(self):
        """
        Less specific IP prefixes/ranges found for the given input resource.

        Returns the list response of strings from the RIPE API due to the various
        possible formats of each line:

        .. code-block:: python

            "193.0.18.0-193.0.21.255",
            "193.0.0.0-193.0.23.255",
            "193.0.0.0/16"

        """
        return self._api.data["less_specifics"]

    @property
    def more_specifics(self):
        """
        More specific IP prefixes/ranges found for the given input resource.

        Returns the list response of strings from the RIPE API due to the various
        possible formats of each line:

        .. code-block:: python

            "193.0.18.0-193.0.21.255",
            "193.0.0.0-193.0.23.255",
            "193.0.0.0/16"

        """
        return self._api.data["more_specifics"]

    @property
    def query_time(self):
        """Holds the time the query was based on."""
        return datetime.fromisoformat(self._api.data["query_time"])

    @property
    def resource(self):
        """Holds the resource the query was based on."""
        return self._resource(self._api.data["resource"])

    @property
    def special_resources(self):
        """List returned from API. No description available."""
        return self._api.data["special_resources"]
