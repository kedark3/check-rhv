# coding: utf-8
"""
These are the functions to check RHV manager/hosts through the
RHV API
"""
from __future__ import division

import sys

from ovirtsdk4 import types

from utils import is_service_in_status
from utils import ssh_client


def check_vm_count(system, warn=20, crit=30, **kwargs):
    """ Check overall host status. """
    logger = kwargs["logger"]
    warn = int(warn)
    crit = int(crit)
    vm_count = len(system.list_vms())
    # determine ok, warning, critical, unknown state
    if vm_count < warn:
        msg = ("Ok: VM count is less than {}. VM Count = {}".format(warn, vm_count))
        logger.info(msg)
        print(msg)
        sys.exit(0)
    elif warn <= vm_count <= crit:
        msg = ("Warning: VM count is greater than {} & less than {}. VM Count = {}"
            .format(warn, crit, vm_count))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif vm_count > crit:
        msg = ("Critical: VM count is greater than {}. VM Count = {}".format(crit, vm_count))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    else:
        msg = ("Unknown: VM count is unknown")
        logger.info(msg)
        print(msg)
        sys.exit(3)


def check_storage_domain_status(system, **kwargs):
    """ Check the usage of all the datastores on the host. """
    logger = kwargs["logger"]
    okay, warning, critical, unknown, all_items = [], [], [], [], []
    storage_domains = system.api.system_service().storage_domains_service().list()

    for storage_domain in storage_domains:
        status = storage_domain.external_status
        if status == types.ExternalStatus.OK:
            okay.append((storage_domain.name, status))
        elif status == types.ExternalStatus.WARNING:
            warning.append((storage_domain.name, status))
        elif status == types.ExternalStatus.FAILURE or status == types.ExternalStatus.ERROR:
            critical.append((storage_domain.name, status))
        else:
            unknown.append((storage_domain.name, status))
        all_items.append((storage_domain.name, status))

    if critical:
        msg = ("Critical: the following storage_domain(s) definitely have an issue: {}\n "
               "Status of all storage_domain is: {}".format(critical, all_items))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    elif warning:
        msg = ("Warning: the following storage_domain(s) may have an issue: {}\n "
               "Status of all storage_domain is: {}".format(warning, all_items))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif unknown:
        msg = ("Unknown: the following storage_domain(s) are in an unknown state: {}\n"
               "Status of all storage_domain is: {}".format(unknown, all_items))
        logger.info(msg)
        print(msg)
        sys.exit(3)
    else:
        msg = ("Ok: all storage_domain(s) are in the OK state: {}".format(okay))
        logger.info(msg)
        print(msg)
        sys.exit(0)


def check_storage_domain_usage(system, warn=0.75, crit=0.9, **kwargs):
    """ Check the usage of all the datastores on the host. """
    logger = kwargs["logger"]
    warn = float(warn)
    crit = float(crit)
    okay, warning, critical, unknown, all_items = [], [], [], [], []
    storage_domains = system.api.system_service().storage_domains_service().list()

    for storage_domain in storage_domains:
        if storage_domain.type == types.StorageDomainType.IMAGE:
            # Skipping storage_domain as it is of type IMAGE
            continue
        used = storage_domain.used
        available = storage_domain.available
        status = used / (used + available)
        sds = system._get_storage_domain_service(storage_domain.name)
        vms = len(sds.vms_service().list())
        if status < warn:
            okay.append((storage_domain.name, status))
        elif warn <= status <= crit:
            warning.append((storage_domain.name, status))
        elif status > crit:
            critical.append((storage_domain.name, status))
        else:
            unknown.append((storage_domain.name, status))
        all_items.append((storage_domain.name, status, vms))

    if critical:
        msg = ("Critical: the following storage_domain(s) definitely have an issue: {}\n "
               "Status of all storage_domain is: {}".format(critical, all_items))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    elif warning:
        msg = ("Warning: the following storage_domain(s) may have an issue: {}\n "
               "Status of all storage_domain is: {}".format(warning, all_items))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif unknown:
        msg = ("Unknown: the following storage_domain(s) are in an unknown state: {}\n"
               "Status of all storage_domain is: {}".format(unknown, all_items))
        logger.info(msg)
        print(msg)
        sys.exit(3)
    else:
        msg = ("Ok: all storage_domain(s) are in the OK state: {}".format(all_items))
        logger.info(msg)
        print(msg)
        sys.exit(0)


def check_locked_disks(system, warn=5, crit=10, **kwargs):
    """Check the count of locked disks."""
    logger = kwargs["logger"]
    warn = int(warn)
    crit = int(crit)
    # following function call is not available in wrapanapi yet, need to merge PR#373
    locked_disks = len(system.list_disks(status='LOCKED'))
    if locked_disks < warn:
        msg = ("Ok: locked_disks count is less than {}. locked_disks Count = {}"
               .format(warn, locked_disks))
        logger.info(msg)
        print(msg)
        sys.exit(0)
    elif warn <= locked_disks <= crit:
        msg = ("Warning: locked_disks count is greater than {}"
              " & less than {}. locked_disks Count = {}"
            .format(warn, crit, locked_disks))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif locked_disks > crit:
        msg = (
            "Critical: locked_disks count is greater than {}. locked_disks Count = {}".format(
                crit, locked_disks
            )
        )
        logger.error(msg)
        print(msg)
        sys.exit(2)
    else:
        msg = ("Unknown: locked_disks count is unknown")
        logger.info(msg)
        print(msg)
        sys.exit(3)


def check_hosts_status(system, **kwargs):
    """ Check the status of all the hosts."""
    logger = kwargs["logger"]
    okay, warning, critical, unknown, all_items = [], [], [], [], []
    hosts = system.api.system_service().hosts_service().list()

    for host in hosts:
        status = host.status
        if status == types.HostStatus.UP:
            okay.append((host.name, status))
        elif (status == types.HostStatus.MAINTENANCE or status == types.HostStatus.UNASSIGNED or
             status == types.HostStatus.REBOOT or status == types.HostStatus.CONNECTING or
             status == types.HostStatus.INITIALIZING):
            warning.append((host.name, status))
        elif (status == types.HostStatus.ERROR or status == types.HostStatus.DOWN or
             status == types.HostStatus.NON_OPERATIONAL or
             status == types.HostStatus.NON_RESPONSIVE):
            critical.append((host.name, status))
        else:
            unknown.append((host.name, status))
        all_items.append((host.name, status))

    if critical:
        msg = ("Critical: the following host(s) definitely have an issue: {}\n "
               "Status of all host is: {}".format(critical, all_items))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    elif warning:
        msg = ("Warning: the following host(s) may have an issue: {}\n "
               "Status of all host is: {}".format(warning, all_items))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif unknown:
        msg = ("Unknown: the following host(s) are in an unknown state: {}\n"
               "Status of all host is: {}".format(unknown, all_items))
        logger.info(msg)
        print(msg)
        sys.exit(3)
    else:
        msg = ("Ok: all host(s) are in the OK state: {}".format(okay))
        logger.info(msg)
        print(msg)
        sys.exit(0)


def check_datacenters_status(system, **kwargs):
    """ Check the status of all the hosts."""
    logger = kwargs["logger"]
    okay, warning, critical, unknown, all_items = [], [], [], [], []
    datacenters = system.api.system_service().data_centers_service().list()

    for datacenter in datacenters:
        status = datacenter.status
        if status == types.DataCenterStatus.UP:
            okay.append((datacenter.name, status))
        elif (status == types.DataCenterStatus.MAINTENANCE or
        status == types.DataCenterStatus.UNINITIALIZED):
            warning.append((datacenter.name, status))
        elif (status == types.DataCenterStatus.PROBLEMATIC or
        status == types.DataCenterStatus.NOT_OPERATIONAL):
            critical.append((datacenter.name, status))
        else:
            unknown.append((datacenter.name, status))
        all_items.append((datacenter.name, status))

    if critical:
        msg = ("Critical: the following datacenter(s) definitely have an issue: {}\n "
               "Status of all datacenter is: {}".format(critical, all_items))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    elif warning:
        msg = ("Warning: the following datacenter(s) may have an issue: {}\n "
               "Status of all datacenter is: {}".format(warning, all_items))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif unknown:
        msg = ("Unknown: the following datacenter(s) are in an unknown state: {}\n"
               "Status of all datacenter is: {}".format(unknown, all_items))
        logger.info(msg)
        print(msg)
        sys.exit(3)
    else:
        msg = ("Ok: all datacenter(s) are in the OK state: {}".format(okay))
        logger.info(msg)
        print(msg)
        sys.exit(0)


def check_storage_domain_attached_status(system, **kwargs):
    """ Check the usage of all the datastores on the host. """
    logger = kwargs["logger"]
    okay, critical, all_items = [], [], []
    storage_domains_service = system.api.system_service().storage_domains_service()
    all_items = storage_domains_service.list()
    data_centers_service = system.api.system_service().data_centers_service()
    all_dc = data_centers_service.list()

    for dc in all_dc:
        dc_service = data_centers_service.data_center_service(dc.id)
        attached_sds_service = dc_service.storage_domains_service()
        for sd in all_items:
            if sd.type == types.StorageDomainType.IMAGE:
                # Skipping sd as it is of type IMAGE
                continue
            attached_sds_service_sd_id = attached_sds_service.storage_domain_service(sd.id)
            status = attached_sds_service_sd_id.get().status
            if status == types.StorageDomainStatus.ACTIVE:
                okay.append((sd.name, status.value))
            else:
                critical.append((sd.name, status.value))
            all_items.append((sd.name, status.value))

    if critical:
        msg = ("Critical: the following Storage Domain(s) definitely have an issue: {}\n "
               "Status of all Storage Domain(s) are: {}".format(critical, all_items))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    else:
        msg = ("Ok: all Storage Domain(s) are Attached to Data Center(s): {}".format(okay))
        logger.info(msg)
        print(msg)
        sys.exit(0)


def check_vms_distributed_hosts(system, warn=5, crit=10, **kwargs):
    """VMs are evenly distributed across the hosts"""
    logger = kwargs["logger"]
    warn = int(warn)
    crit = int(crit)
    # get all the hosts
    hosts = system.api.system_service().hosts_service().list()

    # get number of VMs on each host
    hosts_vms = dict()
    for host in hosts:
        hosts_vms[host.name] = host.summary.total

    # check the difference between the lowest and the highest number
    max_hosts_vms = max(hosts_vms.values())
    min_hosts_vms = min(hosts_vms.values())

    vms_host_diff = max_hosts_vms - min_hosts_vms

    # determine ok, warning, critical, unknown state
    if vms_host_diff < warn:
        msg = ("Ok: VMs difference on hosts is less than {}. VMs difference = {}."
              "The distribution is {}".format(warn, vms_host_diff, hosts_vms))
        logger.info(msg)
        print(msg)
        sys.exit(0)
    elif warn <= vms_host_diff <= crit:
        msg = (
            "Warning: VMs difference on hosts is more than {} & less than {}. VMs difference = {}."
            "The distribution is {}".format(warn, crit, vms_host_diff, hosts_vms))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    elif vms_host_diff > crit:
        msg = ("Critical: VMs difference on hosts is more than {}. VMs difference = {}"
              "The distribution is {}".format(crit, vms_host_diff, hosts_vms))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    else:
        msg = ("Unknown: VMs on hosts are unknown")
        logger.info(msg)
        print(msg)
        sys.exit(3)


def check_hosted_engine_status(system, **kwargs):
    """ Check the status of all the host's Hosted Engine Status."""
    logger = kwargs["logger"]
    okay, critical, warning, all_items = [], [], [], []
    # Get all the hosts with details.
    hosts = system.api.system_service().hosts_service().list(all_content=True)

    for host in hosts:
        host_info = {
            "Configured": host.hosted_engine.configured,
            "Active": host.hosted_engine.active,
            "local_maintenance": host.hosted_engine.local_maintenance,
            "global_maintenance": host.hosted_engine.global_maintenance,
            "Score": host.hosted_engine.score,
        }
        engine_value = all((host_info["Active"], host_info["Configured"]))
        maintenance_value = any(
            (host_info["global_maintenance"], host_info["local_maintenance"])
        )
        if not engine_value or maintenance_value:
            critical.append((host.name, host_info))
        else:
            okay.append((host.name, host_info))
        # Checking hosted engine non-zero scrore.
        if host_info["Score"] < 3400:
            warning.append((host.name, host_info["Score"]))
        all_items.append((host.name, host_info))

    if critical:
        msg = ("Critical: The following host's hosted-engine status has an issue: {state}\n "
            "Status of all host is: {all_items}".format(state=critical, all_items=all_items))
        logger.error(msg)
        print(msg)
        sys.exit(2)
    elif warning:
        msg = ("Warning: The following host's hosted-engine score reported below 3400.\n "
            "Actual scrore of host is {}".format(warning))
        logger.warning(msg)
        print(msg)
        sys.exit(1)
    else:
        msg = ("Ok: all host(s) hosted-engine status is in the OK state: {}".format(okay))
        logger.info(msg)
        print(msg)
        sys.exit(0)


def check_services_status(system, **kwargs):
    """Check to see if service are in the desired state"""
    logger = kwargs["logger"]
    kwargs.pop("logger", None)
    hosts = system.api.system_service().hosts_service()
    hosts_agents = dict()
    hosts_status = dict()

    for host in hosts.list():
        host_service = hosts.host_service(host.id)
        ssh = ssh_client(host_service, username="root", password=system.api._password)
        with ssh:
            for service_name, status in kwargs.iteritems():
                service_status = is_service_in_status(ssh, service_name, status)
                try:
                    hosts_agents[host.name].update({service_name: service_status})
                except KeyError:
                    hosts_agents[host.name] = {service_name: service_status}

        hosts_status[host.name] = all(hosts_agents[host.name].values())

    overall_status = all(hosts_status.values())

    # TODO: add the exact desired state in message instead of True/False
    if overall_status:  # all true, everything is running
        msg = ("Ok: all services {} are in the desired state on all hosts".format(kwargs.keys()))
        logger.info(msg)
        print(msg)
        sys.exit(0)
    else:
        trouble_hosts = [host for host, status in hosts_status.iteritems() if not status]
        msg = ("Critical: These hosts don't have all agents in the desired state: {}."
               "Overall status is {}".format(trouble_hosts, hosts_agents))
        logger.info(msg)
        print(msg)
        sys.exit(2)


CHECKS = {
    "vm_count": check_vm_count,
    "storage_domain_status": check_storage_domain_status,
    "storage_domain_usage": check_storage_domain_usage,
    "locked_disks_count": check_locked_disks,
    "hosts_status": check_hosts_status,
    "datacenter_status": check_datacenters_status,
    "storage_domain_attached": check_storage_domain_attached_status,
    "vms_distributed_hosts": check_vms_distributed_hosts,
    "hosted_engine_status": check_hosted_engine_status,
    "services_status": check_services_status,
    }
