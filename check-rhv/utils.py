# coding: utf-8
"""
Helper functions
"""
from _socket import timeout

import paramiko


def host_ips(host_service):
    """
    Helper function for check_services_status to find an ip of the host to connect to.
    This is a workaround of the following issues in Paramiko library:
    https://github.com/paramiko/paramiko/issues/686
    https://github.com/paramiko/paramiko/issues/770
    """
    nics = host_service.nics_service().list()
    # return only ips 'startswith("10.")' to catch local network ipv4
    return [n.ip.address for n in nics if n.ip is not None and n.ip.address.startswith("10.")]


def ssh_client(host_service, username, password):
    """
    SSH client with a workaround for using IPv4 addresses
    """
    ip_addresses = host_ips(host_service)
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    for ip in ip_addresses:
        try:
            ssh.connect(ip, username=username, password=password, timeout=60)
            return ssh
        except timeout:
            continue
    if ssh.get_transport() is None:
        # An SSH Transport attaches to a stream (usually a socket), negotiates an encrypted session,
        # authenticates, and then creates stream tunnels, called channels, across the session.
        # If connection is not established, returns None.
        raise timeout("No pingable IP found")


def get_services_status_list(ssh):
    """
    We are retireving information of 'vdsmd' and 'ovirt-ha-agent' service from given host
    and returns in dict contains status.

    systemctl command below returns output in following format:----->
    ovirt-ha-agent.service loaded active running oVirt Hosted Engine High Availability 
    Monitoring Agent
    vdsmd.service          loaded active running Virtual Desktop Server Manager
    awk command will slice it and conver it to this format:----->
    ['ovirt-ha-agent.service: active (running)\n',
    'supervdsmd.service: active (running)\n',
    'vdsmd.service: active (running)\n']
    And the return statement has code to convert it to a dictionary of kind:----->
    {'ovirt-ha-agent.service': ' active (running)',
    'supervdsmd.service': ' active (running)',
    'vdsmd.service': ' active (running)'}

    """

    stdin, stdout, stderr = ssh.exec_command("systemctl list-units --type service --all"
                                            " --no-page   --no-legend | "
                                            "awk -F ' ' '{print $1 \": \" $3 \" (\" $4\")\"}'"
                                            " | egrep 'vdsmd|ovirt-ha-agent'")
    return {line.split(":")[0]: line.split(":")[1].replace("\n", "") for line in stdout.readlines()}
