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
