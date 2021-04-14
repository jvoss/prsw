import argparse
import ipaddress

import rsaw

def args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-a", "--asn", type=str, required=True, help="Autonomous System Number"
    )
    parser.add_argument(
        "-p", "--prefix", required=True, type=str, help="Prefix to validate"
    )

    args = parser.parse_args()

    # Validate Prefix is a valid IP prefix
    if args.prefix:
        prefixes = []

        try:
            for prefix in args.prefix.split(","):
                prefixes.append(ipaddress.ip_network(prefix, strict=False))

        except ValueError as e:
            print(e)
            parser.print_help()
            exit()

        args.prefix = prefixes

    return args


def main():
    # Parse arguments
    cli = args()
    ripe = rsaw.RIPEstat()

    # Pull all prefixes for an ASN if needed
    if not cli.prefix:
        prefixes = ripe.announced_prefixes(cli.asn)
    else:
        prefixes = cli.prefix

    for prefix in prefixes:
        resp = ripe.rpki_validation_status(cli.asn, prefix)
        status = resp.status
        roas = resp.validating_roas

        print()
        print("=" * 80)
        print(prefix)
        print("=" * 80)
        print()
        print(f"RPKI Status: {status}")

        if roas:
            print()
            print("ROAs:")

            line = 0

            fmt = "{:<4} {:<10} {:<20} {:<5} {:<10} {}"
            print(fmt.format("#", "Origin", "Prefix", "Max", "Validity", "Source"))
            print("-" * 80)

            for roa in roas:
                print(
                    fmt.format(
                        line,
                        roa.origin,
                        str(roa.prefix),
                        roa.max_length,
                        roa.validity,
                        roa.source,
                    )
                )
                line += 1

        print()


if __name__ == "__main__":
    main()
