import os
import unittest

import testinfra.utils.ansible_runner
from ddt import ddt, idata

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def host_generator():
    for hostname in testinfra_hosts:
        yield hostname


FAILOVER_PUBLIC_IP = "154.222.4.34"
FAILOVER_PRIVATE_IP = "192.168.200.250"


@ddt
class RescueModeTest(unittest.TestCase):

    @idata(host_generator())
    def test_keepalived_config_exists(self, hostname):
        host = testinfra.get_host("docker://" + hostname)
        f = host.file('/etc/keepalived/keepalived.conf')

        assert f.exists
        assert f.user == 'root'
        assert f.group == 'root'

    @idata(host_generator())
    def test_keepalived_installed_and_running(self, hostname):
        host = testinfra.get_host("docker://" + hostname)

        package = host.package("keepalived")
        assert package.is_installed

        keepalived_procs_cmd = host.run("pgrep keepalived | wc -l")
        keepalived_procs = int(keepalived_procs_cmd.stdout.strip())

        assert keepalived_procs > 0

    def test_keepalived_initial_state(self):
        host_master = testinfra.get_host("docker://keepalived1")
        host_backup = testinfra.get_host("docker://keepalived2")

        state_cmd = "cat /var/run/keepalived.hetzner_failover_ip.state"
        master_status_cmd = host_master.run(state_cmd)
        master_status = master_status_cmd.stdout.strip()

        backup_status_cmd = host_backup.run(state_cmd)
        backup_status = backup_status_cmd.stdout.strip()

        assert master_status == "MASTER"
        assert backup_status == "BACKUP"

        pub_ip_cmd = "ip addr | grep '" + FAILOVER_PUBLIC_IP + "' | wc -l"
        priv_ip_cmd = "ip addr | grep '" + FAILOVER_PRIVATE_IP + "' | wc -l"

        master_pub_ip_cmd = host_master.run(pub_ip_cmd)
        master_pub_ip_count = int(master_pub_ip_cmd.stdout.strip())

        master_priv_ip_cmd = host_master.run(priv_ip_cmd)
        master_priv_ip_count = int(master_priv_ip_cmd.stdout.strip())

        backup_pub_ip_cmd = host_backup.run(pub_ip_cmd)
        backup_pub_ip_count = int(backup_pub_ip_cmd.stdout.strip())

        backup_priv_ip_cmd = host_backup.run(priv_ip_cmd)
        backup_priv_ip_count = int(backup_priv_ip_cmd.stdout.strip())

        assert master_pub_ip_count == 1
        assert master_priv_ip_count == 1
        assert backup_pub_ip_count == 0
        assert backup_priv_ip_count == 0
