import argparse
import ipaddress
import json
import ripe

from json import JSONEncoder

class BGPPrefix:
  def __init__(self, **kwargs):
    self.asn_origin   = kwargs['asn_origin']
    self.as_path      = kwargs['as_path']
    self.community    = kwargs['community']
    self.last_updated = kwargs['last_updated']
    self.prefix       = kwargs['prefix']
    self.peer         = kwargs['peer']
    self.origin       = kwargs['origin']
    self.next_hop     = kwargs['next_hop']
    self.latest_time  = kwargs['latest_time']


class BGPEncoder(JSONEncoder):
  def default(self, o):
    return o.__dict__


def args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-a", "--asn",    type=str, help="Routes for ASN")
  parser.add_argument("-p", "--prefix", type=str, help="Limit to specified prefix(s)")

  args = parser.parse_args()

  # Require ASN or Prefix be specified at a minimum 
  if args.asn == None and args.prefix == None:
    parser.print_help()
    exit()

  # Validate Prefix is a valid IP prefix
  if args.prefix:
    prefixes = []

    try:
      for prefix in args.prefix.split(','):
        prefixes.append(ipaddress.ip_network(prefix, strict=False))

    except:
      print('Invalid IPv4 or IPv6 prefix')
      parser.print_help()
      exit()

    args.prefix = prefixes

  return args


def get_prefixes(asn):
  prefixes = []

  resp = ripe.announced_prefixes(asn)

  for prefix in resp['data']['prefixes']:
    prefixes.append(ipaddress.ip_network(prefix['prefix']))

  return prefixes


def get_paths(prefix):
  locations = {}

  resp = ripe.looking_glass(prefix)

  for rrcs in resp['data']['rrcs']:
    location = rrcs['location']

    locations[rrcs['location']] = {}
    locations[rrcs['location']]['peers'] = []

    for peer in rrcs['peers']:
      locations[location]['peers'].append(BGPPrefix(**peer))

  return locations


def main():
  # Parse arguments
  cli = args()

  paths    = {}
  prefixes = []

  if not cli.prefix:
    prefixes = get_prefixes(cli.asn)
  else:
    prefixes = cli.prefix

  # Get paths for each prefixes
  for prefix in prefixes:
    paths[str(prefix)] = get_paths(prefix)

  # Write baseline file for prefixes
  # with open('baseline.json', 'w') as file:
  #   file.write(BGPEncoder().encode(paths))

  # Print report for all prefixes
  for prefix,route_server in paths.items():
    print()
    print('=' * 80)
    print(prefix)
    print('=' * 80)
    print()

    for location,peers in route_server.items():
      line = 0

      print("Route Server: " + location)
      fmt = '{:<4} {:<30} {}'
      print(fmt.format('#', 'Router ID', 'AS PATH'))
      print('-' * 80)
      for peer in peers['peers']:
        print(fmt.format(line, peer.peer, peer.as_path))
        line += 1

      print()


if __name__ == '__main__':
  main()
