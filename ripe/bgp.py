import datetime

from collections import namedtuple
from typing import Optional
from ._common import _get

from ripe import Output


def announced_prefixes(
    resource,
    starttime: Optional[datetime.datetime] = None,
    endtime: Optional[datetime.datetime] = None,
    min_peers_seeing=None,
):
    """
    This data call returns all announced prefixes for a given ASN. The results
    can be restricted to a specific time period.

    Arguments:
        resource {str}         -- The Autonomous System Number for which to
                                  return prefixes.

    Keyword Arguments:
        starttime {timestamp}  -- The start time for the query. (defaults to two
                                  weeks before current date and time)

        endtime {timestamp}    -- The end time for the query. (defaults to now)

        min_peers_seeing {int} -- Minimum number of RIS peers seeing the prefix for
                                  it to be included in the results. Excludes low
                                  visibility/localized announcements. (default 10)

    Returns:
        AnnouncedPrefixes --
    """
    url = "/announced-prefixes/"
    params = "resource=" + str(resource)

    if starttime:
        if isinstance(starttime, datetime.datetime):
            params += "&starttime=" + str(starttime)
        else:
            raise ValueError("starttime expected to be datetime")
    if endtime:
        if isinstance(endtime, datetime.datetime):
            params += "&endtime=" + str(endtime)
        else:
            raise ValueError("endtime expected to be datetime")
    if min_peers_seeing:
        if isinstance(min_peers_seeing, int):
            params += "&min_peers_seeing=" + str(min_peers_seeing)
        else:
            raise ValueError("min_peers_seeing expected to be int")

    
    return _get(url, params)
