# coding: utf-8
"""
Helper functions
"""
from _socket import timeout

import paramiko


def is_service_in_status(ssh, name, expected_status):
    """Helper function for check_services_status to check a specific service's status"""
    stdin, stdout, stderr = ssh.exec_command("systemctl status {}".format(name))
    output = stdout.read()
    status = output.decode('utf-8').strip()
    return expected_status in status


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
