import os

import testinfra.utils.ansible_runner

testinfra_hosts = testinfra.utils.ansible_runner.AnsibleRunner(
    os.environ['MOLECULE_INVENTORY_FILE']
).get_hosts('all')


def test_keepalived_config_exists(host):
    f = host.file('/etc/keepalived/keepalived.conf')

    assert f.exists
    assert f.user == 'root'
    assert f.group == 'root'


def test_keepalived_installed_and_running(host):
    package = host.package("keepalived")
    assert package.is_installed

    service = host.service("keepalived")
    assert service.is_running
    assert service.is_enabled
