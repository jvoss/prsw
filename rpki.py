import argparse
import ipaddress
import json
import ripe

def args():
  parser = argparse.ArgumentParser()
  parser.add_argument("-a", "--asn",    type=str, required=True, help="Autonomous System Number")
  parser.add_argument("-p", "--prefix", type=str, help="Prefix to validate")

  args = parser.parse_args()

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


def main():
  # Parse arguments
  cli = args()

  # Pull all prefixes for an ASN if needed
  if not cli.prefix:
    prefixes = get_prefixes(cli.asn)
  else:
    prefixes = cli.prefix

  for prefix in prefixes:
    resp   = ripe.rpki_validation(cli.asn, prefix)
    status = resp['data']['status']
    roas   = resp['data']['validating_roas'] 

    print()
    print('=' * 80)
    print(prefix)
    print('=' * 80)
    print()
    print(f"RPKI Status: {status}")

    if roas:
      print()
      print(f'ROAs:')

      line = 0

      fmt = '{:<4} {:<10} {:<20} {:<5} {:<10} {}'
      print(fmt.format('#', 'Origin', 'Prefix', 'Max', 'Validity', 'Source'))
      print('-'*80)

      for roa in roas:
        print(fmt.format(line, roa['origin'], roa['prefix'], roa['max_length'], roa['validity'], roa['source']))
        line += 1

    print()


if __name__ == "__main__":
  main()