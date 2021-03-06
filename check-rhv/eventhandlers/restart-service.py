#!/usr/bin/env python
"""
Event handler to restart a service via ansible, requires ansible to be installed on the shinken
server.
"""

import argparse
import subprocess


def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        "-H",
        "--hostname",
        dest="hostname",
        help="Hostname of Client",
        type=str,
    )
    parser.add_argument(
        "-S",
        "--service",
        dest="service",
        help="Service desired for restart",
        type=str,
    )
    parser.add_argument(
        "-s",
        "--state",
        dest="state",
        help="State of the check (e.g. 'OK', 'WARNING', 'CRITICAL')",
        type=str,
    )
    parser.add_argument(
        "-t",
        "--type",
        dest="type",
        help="Type of the state ('HARD' or 'SOFT')",
        type=str,
    )
    parser.add_argument(
        "-a",
        "--attempt",
        dest="attempt",
        help="Attempt number on the service check",
        type=int
    )
    parser.add_argument(
        "-m",
        "--max-attempts",
        dest="max_attempts",
        help="Number of max attempts allowed on the service check",
        type=int,
        default=3
    )
    parser.add_argument(
        "-d",
        "--directory",
        dest="directory",
        help="Directory from which to run the command, usually where ansible config files reside.",
        type=str,
        default="/etc/shinken/ansible"
    )
    args = parser.parse_args()

    # we want to restart the service if it is in a critical SOFT state and has been checked
    #   the max number of times, i.e. right before it notifies for human intervention OR
    #   if the service somehow entered a HARD state
    if (
        (args.state == "CRITICAL" and args.type == "SOFT" and args.attempt >= args.max_attempts) or
        (args.state == "CRITICAL" and args.type == "HARD")
    ):
        # call ansible script to restart the service
        command = [
            "ansible",
            args.hostname,
            "-m",
            "service",
            "-a",
            "name={} state=restarted".format(args.service)
        ]
        output = subprocess.check_output(command, universal_newlines=True, cwd=args.directory)
        print(output)
    else:
        # do nothing otherwise
        return


if __name__ == "__main__":
    main()
