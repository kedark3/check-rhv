# coding: utf-8
"""
These are the functions to check RHV manager/hosts through the
RHV API
"""
import sys


def check_vm_count(system, warn=20, crit=30, **kwargs):
    """ Check overall host status. """
    warn = int(warn)
    crit = int(crit)
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


def check_storage_domain_status(system, **kwargs):
    """ Check the usage of all the datastores on the host. """
    okay, warning, critical, unknown, all = [], [], [], [], []
    storage_domains = system.api.system_service().storage_domains_service().list()

    for storage_domain in storage_domains:
        status = storage_domain.external_status.name
        if status == "OK":
            okay.append((storage_domain.name, status))
        elif status == "WARNING":
            warning.append((storage_domain.name, status))
        elif status == "FAILURE" or status == "ERROR":
            critical.append((storage_domain.name, status))
        else:
            unknown.append((storage_domain.name, status))
        all.append((storage_domain.name, status))

    if critical:
        print("Critical: the following storage_domain(s) definitely have an issue: {}\n "
              "Status of all storage_domain is: {}".format(critical, all))
        sys.exit(2)
    elif warning:
        print("Warning: the following storage_domain(s) may have an issue: {}\n "
              "Status of all storage_domain is: {}".format(warning, all))
        sys.exit(1)
    elif unknown:
        print("Unknown: the following storage_domain(s) are in an unknown state: {}\n"
              "Status of all storage_domain is: {}".format(unknown, all))
        sys.exit(3)
    else:
        print("Ok: all storage_domain(s) are in the OK state: {}".format(okay))
        sys.exit(0)

CHECKS = {
    "vm_count": check_vm_count,
    "storage_domain_status": check_storage_domain_status,
}
