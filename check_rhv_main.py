#!/usr/bin/env python
# coding: utf-8
"""
This script performs checks for Red Hat Virtualization(RHV) hosts/Manager through the
RHV API.
"""
import argparse
import json
import sys

from argparse import RawTextHelpFormatter
from rhv_checks import CHECKS
from rhv_logconf import get_logger
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
        default=0.75,
    )
    parser.add_argument(
        "-c",
        "--critical",
        dest="critical",
        help="Critical value. Could be fraction or whole number.",
        type=float,
        default=0.9,
    )
    parser.add_argument(
        "-l",
        "--local",
        dest="local",
        help="Use this field when testing locally",
        action="store_true",
        default=False
        )
    parser.add_argument(
        "-s",
        "--services",
        dest="services",
        help="Dictionary of services and their expected statuses",
        type=str,
    )
    args = parser.parse_args()
    # set logger
    logger = get_logger(args.local)

    if args.warning > args.critical:
        logger.error("Error: warning value can not be greater than critical value")
        print("Error: warning value cannot be greater than critical value")
        sys.exit(3)

    # connect to the system
    logger.info("Connecting to RHV %s as user %s", args.rhvm, args.user)
    system = RHEVMSystem(args.rhvm, args.user, args.password, version=4.3)
    # get measurement function
    measure_func = get_measurement(args.measurement)
    if not measure_func:
        logger.error("Error: measurement {} not understood".format(args.measurement))
        print("Error: measurement {} not understood".format(args.measurement))
        sys.exit(3)

    # run the measurement function
    # if warning and critical values are not set, we need to use the default and not pass them
    try:
        logger.info("Calling check %s", measure_func.__name__)
        if args.services:
            measure_func(system,
                         logger=logger,
                         services=json.loads(args.services.replace("'", "\"")))
        else:
            measure_func(system, warn=args.warning, crit=args.critical, logger=logger)
    except Exception as e:
        logger.error(
            "Exception occurred during execution of %s",
            measure_func.__name__,
            exc_info=True
        )
        print(
            "ERROR: exception '{}' occurred during execution of '{}', check logs for trace".format(
                e,
                measure_func.__name__
            )
        )
        sys.exit(3)


if __name__ == "__main__":
    main()
