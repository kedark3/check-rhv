# coding: utf-8
"""
These are the functions to check RHV manager/hosts through the
RHV API
"""
import sys


def check_vm_count(system, warn=20, crit=30, **kwargs):
    """ Check overall host status. """
    vm_count = len(system.list_vms())
    # determine ok, warning, critical, unknown state
    if vm_count < warn:
        print("Ok: VM count is less than {}. VM Count = {}".format(warn, vm_count))
        sys.exit(0)
    elif vm_count > warn and vm_count < crit:
        print("Warning: VM count is greater than {} & less than {}. VM Count = {}"
            .format(warn, crit, vm_count))
        sys.exit(1)
    elif vm_count > crit:
        print("Critical: VM count is greate than crit. VM Count = {}".format(crit, vm_count))
        sys.exit(2)
    else:
        print("Unknown: VM count is unknown")
        sys.exit(3)

CHECKS = {
    "vm_count": check_vm_count,
}
