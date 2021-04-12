import argparse
import ipaddress

from rsaw import announced_prefixes
from rsaw import looking_glass


def args():
    parser = argparse.ArgumentParser()
    parser.add_argument("-a", "--asn", type=str, help="Routes for ASN")
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
            for prefix in args.prefix.split(","):
                prefixes.append(ipaddress.ip_network(prefix, strict=False))

        except:
            print("Invalid IPv4 or IPv6 prefix")
            parser.print_help()
            exit()

        args.prefix = prefixes

    return args


def main():
    # Parse arguments
    cli = args()

    paths = {}
    prefixes = []

    if not cli.prefix:
        for prefix in announced_prefixes(cli.asn):
            prefixes.append(prefix.prefix)
    else:
        prefixes = cli.prefix

    # Get paths for each prefixes
    for prefix in prefixes:
        paths[str(prefix)] = looking_glass(prefix)

    # Write baseline file for prefixes
    # with open('baseline.json', 'w') as file:
    #   file.write(BGPEncoder().encode(paths))

    # Print report for all prefixes
    for prefix, collectors in paths.items():
        print()
        print("=" * 80)
        print(prefix)
        print("=" * 80)
        print()

        for collector in collectors:
            line = 0

            print("Route Server: " + collector.location)
            fmt = "{:<4} {:<30} {}"
            print(fmt.format("#", "Router ID", "AS PATH"))
            print("-" * 80)
            for peer in collector.peers:
                print(
                    fmt.format(line, str(peer.peer), " ".join(map(str, peer.as_path)))
                )
                line += 1

            print()


if __name__ == "__main__":
    main()
