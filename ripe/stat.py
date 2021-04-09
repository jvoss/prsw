import requests

RIPE_URL = 'https://stat.ripe.net/data'


class RIPEError(Exception):
  """GenericError Class for RIPE API Errors."""


def _get(url, params):
  url = RIPE_URL + str(url) + 'data.json?' + str(params)
  r = requests.get(url)

  return r.json()


def announced_prefixes(resource, **kwargs):
  """
  This data call returns all announced prefixes for a given ASN. The results 
  can be restricted to a specific time period. 

  Arguments:
    resource {str}         -- The Autonomous System Number for which to return 
                              prefixes.

  Keyword Arguments:
    starttime {timestamp}  -- The start time for the query. (defaults to two 
                              weeks before current date and time)

    endtime {timestamp}    -- The end time for the query. (defaults to now)

    min_peers_seeing {int} -- Minimum number of RIS peers seeing the prefix for
                              it to be included in the results. Excludes low
                              visibility/localized announcements. (default 10)
  """

  url    = '/announced-prefixes/'
  params = 'resource=' + str(resource)

  for key, value in kwargs.items():
    params += f'&{key}={value}'

  return _get(url, params)


# def bgp_state(resource):
#   url    = '/bgp-state/'
#   params = 'resource=' + str(resource)

#   return _get(url, params)


def looking_glass(resource):
  """
  This data call returns information commonly coming from a Looking Glass. The 
  data is based on a data feed from the RIPE NCC's network of BGP route 
  collectors (RIS, see https://www.ripe.net/data-tools/stats/ris for more 
  information). The data processing usually happens with a small delay and can 
  be considered near real-time. The output is structured by collector node (RRC)
  accompanied by the location and the BGP peers which provide the routing 
  information. 

  Arguments:
    resource {str} -- A prefix or an IP address.

  Returns:
    Dict[rrcs] -- 
  """

  url    = '/looking-glass/'
  params = 'resource=' + str(resource) 

  return _get(url, params)


def rpki_validation(resource, prefix):
  """
  This data call returns the RPKI validity state for a combination of prefix 
  and Autonomous System. This combination will be used to perform the lookup 
  against the RIPE NCC's RPKI Validator, and then return its RPKI validity 
  state.

  Arguments:
    resource {str} -- The ASN used to perform the RPKI validity state lookup.
    prefix {str}   -- The prefix to perform the RPKI validity state lookup. Note
                      the prefix's length is also taken from this field.
  
  Returns:
    Dict
  """

  url    = '/rpki-validation/'
  params = 'resource=' + str(resource) + '&prefix=' + str(prefix)

  return _get(url, params)


if __name__ == '__main__':
  print('Sorry, this is just a library')
  quit()
