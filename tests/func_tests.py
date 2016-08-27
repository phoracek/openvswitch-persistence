"""Functional tests for openvswitch-persistence.

Requires openvswitch-persistence to be installed and enabled. Tests can be
executed via pytest.
"""
from subprocess import check_call, check_output


_OVS_VSCTL = '/usr/bin/ovs-vsctl'
_SYSTEMCTL = '/usr/bin/systemctl'

_BRIDGE = 'testbr0'
_PORT = 'testport0'


class TestRemovalOfNonPersistentDevices(object):

    def setup_method(self, method):
        _systemctl('start', 'openvswitch')

    def teardown_method(self, method):
        _ovs_vsctl(['--if-exists', 'del-br', _BRIDGE])

    def test_bridge(self):
        _ovs_vsctl([
            'add-br', _BRIDGE, '--',
            'set', 'Bridge', _BRIDGE, 'other_config:persistent=false', '--',
            'add-port', _BRIDGE, _PORT, '--',
            'set', 'Interface', _PORT, 'type=internal'])
        _systemctl('restart', 'openvswitch')
        bridges = _ovs_vsctl(['list-br'])
        assert _BRIDGE not in bridges

    def test_port(self):
        _ovs_vsctl([
            'add-br', _BRIDGE, '--',
            'add-port', _BRIDGE, _PORT, '--',
            'set', 'Port', _PORT, 'other_config:persistent=false', '--',
            'set', 'Interface', _PORT, 'type=internal'])
        _systemctl('restart', 'openvswitch')
        bridges = _ovs_vsctl(['list-br'])
        assert _BRIDGE in bridges
        ports = _ovs_vsctl(['list-ports', _BRIDGE])
        assert _PORT not in ports


def _systemctl(action, service):
    check_call([_SYSTEMCTL, action, service])


def _ovs_vsctl(args_list):
    return check_output([_OVS_VSCTL] + args_list, universal_newlines=True)
