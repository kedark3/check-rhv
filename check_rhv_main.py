#!/usr/bin/env python
# coding: utf-8
"""
This script performs checks for Red Hat Virtualization(RHV) hosts/Manager through the
RHV API.
"""

import argparse
import sys

from argparse import RawTextHelpFormatter
from rhv_checks import CHECKS
from wrapanapi.systems.rhevm import RHEVMSystem


def get_measurement(measurement):
    return CHECKS.get(measurement, None)


def main():
    parser = argparse.ArgumentParser(formatter_class=RawTextHelpFormatter)
    parser.add_argument(
        "-R",
        "--rhv-maanager-url",
        dest="rhvm",
        help="Hostname of RHV Manager",
        type=str
    )
    parser.add_argument(
        "-u",
        "--user",
        dest="user",
        help="remote user to use",
        type=str,
    )
    parser.add_argument(
        "-p",
        "--password",
        dest="password",
        help="password for vSphere client",
        type=str
    )
    parser.add_argument(
        "-m",
        "--measurement",
        dest="measurement",
        help="Type of measurement to carry out",
        type=str
    )
    parser.add_argument(
        "-w",
        "--warning",
        dest="warning",
        help="Warning value. Could be fraction or whole number.",
        type=float,
        default=0.75
    )
    parser.add_argument(
        "-c",
        "--critical",
        dest="critical",
        help="Critical value. Could be fraction or whole number.",
        type=float,
        default=0.9
    )
    args = parser.parse_args()
    if float(args.warning) > float(args.critical):
        print("Error: warning value can not be greater than critical value")
        sys.exit(3)

    # connect to the system
    system = RHEVMSystem(args.rhvm, args.user, args.password, version=4.3)
    # get measurement function
    measure_func = get_measurement(args.measurement)
    if not measure_func:
        print("Error: measurement {} not understood".format(args.measurement))
        sys.exit(3)
    # run the measurement function
    measure_func(system, warn=args.warning, crit=args.critical)


if __name__ == "__main__":
    main()
