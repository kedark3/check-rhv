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
        "--rhv-manager-url",
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
    )
    parser.add_argument(
        "-c",
        "--critical",
        dest="critical",
        help="Critical value. Could be fraction or whole number.",
        type=float,
    )
    args = parser.parse_args()
    if args.warning is not None and args.critical is not None and \
            float(args.warning) > float(args.critical):
        print("Error: warning value can not be greater than critical value")
        sys.exit(3)
    elif (args.warning is None and args.critical is not None) or \
            (args.warning is not None and args.critical is None):
        print("Error: please provide both warning and critical values or use default values."
              "You provided only {}".format("warning" if args.warning is not None else "critical"))
        sys.exit(3)

    # connect to the system
    system = RHEVMSystem(args.rhvm, args.user, args.password, version=4.3)
    # get measurement function
    measure_func = get_measurement(args.measurement)
    if not measure_func:
        print("Error: measurement {} not understood".format(args.measurement))
        sys.exit(3)

    # run the measurement function
    # if warning and critical values are not set, we need to use the default and not pass them
    if args.warning is None and args.critical is None:
        measure_func(system)
    else:
        measure_func(system, warn=args.warning, crit=args.critical)


if __name__ == "__main__":
    main()
