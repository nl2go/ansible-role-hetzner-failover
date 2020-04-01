[![Build Status](https://travis-ci.com/nl2go/ansible-role-hetzner-failover.svg?branch=master)](https://travis-ci.com/nl2go/ansible-role-hetzner-failover)
[![Ansible Galaxy](https://img.shields.io/badge/role-nl2go.hetzner_failover-blue.svg)](https://galaxy.ansible.com/nl2go/hetzner_failover/)
[![GitHub tag (latest by date)](https://img.shields.io/github/v/tag/nl2go/ansible-role-hetzner-failover)](https://galaxy.ansible.com/nl2go/hetzner_failover)
[![Ansible Galaxy Downloads](https://img.shields.io/ansible/role/d/46553.svg?color=blue)](https://galaxy.ansible.com/nl2go/hetzner_failover/)

# Ansible Role: Hetzner failover using a vSwitch and keepalived

An Ansible Role that was inspired by [an article about hetzner failover](https://dtone.engineering/2019/from_failovers_to_keepalived_over_vswitches_with_hetzner/) by @dtone. It aims to deploy a highly available setup of 2 servers sharing a single IP by utilizing [hetzner vSwitch](https://wiki.hetzner.de/index.php/Vswitch/en) and keepalived. The role should be used together with the [nl2go vSwitch role](https://github.com/nl2go/ansible-role-hetzner-vswitch) for setting up the vSwitch. It needs an extra IP subnet with public IP adresses to be ordered for the configured vSwitch. The role does *NOT* utilize the failover IP service provided by hetzner.

## Prerequisites

- Existing [Hetzner Online GmbH Account](https://accounts.hetzner.com).
- Configured [Hetzner Robot Webservice Account](https://robot.your-server.de/preferences).

## Configuration

The following configuration fragments show the setup of a vSwitch named failover with the vlan id `4023` using private adresses from the `192.168.100.0/24` subnet and the IP `154.222.4.34` from the additional IP subnet `154.222.4.32/29` as failover IP. The additional subnet has to be ordered manually after the vSwitch is created by the vSwitch role.

### vSwitch configuration  

vSwitch configuration according to the [vSwitch role](https://github.com/nl2go/ansible-role-hetzner-vswitch):

```yaml
hetzner_vswitch_instances:
- name: failover
    vlan: 4023
    ipv4_address: 192.168.200.0
    ipv4_netmask: 255.255.255.0
```

### keepalived configuration  

```yaml
hetzner_failover_keepalived_public_virtual_router_id: 42

hetzner_failover_keepalived_public_ipaddress: 154.222.4.34 # single IP from the additional IP subnet used as failover IP
hetzner_failover_keepalived_public_network_prefix: 29 # netmask prefix of the additional IP subnet
hetzner_failover_keepalived_public_default_gateway: 154.222.4.33 # gateway IP of the additional IP subnet

hetzner_failover_keepalived_vswich_id: 4023 # should match the vlan id configured in hetzner_vswitch_instances
```

### hosts configuration

```yaml
all:
  hosts:
    keepalived-test-1:
      ansible_host: 123.124.125.1 # main IP of host 1
      hetzner_vswitch_host:
        - name: failover
          ipv4_address: 192.168.200.1 # vSwitch IP of host 1
      hetzner_failover_keepalived_state: MASTER
      hetzner_failover_keepalived_vswitch_ip: 192.168.200.1 # IP of the host in the vSwitch VLAN has to be repeated here
      hetzner_failover_keepalived_peer_ip: 192.168.200.2 # vSwitch IP of the host keepalived should peer with
    keepalived-test-2:
      ansible_host: 123.124.125.2 # main IP of host 2
      hetzner_vswitch_host:
        - name: failover
          ipv4_address: 192.168.200.2 # vSwitch IP of host 2
      hetzner_failover_keepalived_state: BACKUP
      hetzner_failover_keepalived_vswitch_ip: 192.168.200.2 # IP of the host in the vSwitch VLAN has to be repeated here
      hetzner_failover_keepalived_peer_ip: 192.168.200.1 # vSwitch IP of the host keepalived should peer with
```

## Dependencies

None.

## Example Playbook

```yaml
- hosts: all
  roles:
    - nl2go.hetzner_vswitch
    - nl2go.hetzner_failover
```

## Development

Use [docker-molecule](https://github.com/nl2go/docker-molecule) following the instructions to run [Molecule](https://molecule.readthedocs.io/en/stable/)
or install [Molecule](https://molecule.readthedocs.io/en/stable/) locally (not recommended, version conflicts might appear).

Use following to run tests:

    molecule test --all

## Maintainers

- [dirkaholic](https://github.com/dirkaholic)

## License

See the [LICENSE.md](LICENSE.md) file for details.

## Author Information

This role was created by in 2020 by [Newsletter2Go GmbH](https://www.newsletter2go.com/).
