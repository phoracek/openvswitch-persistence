#!/usr/bin/env python
# openvswitch-persistence - Open vSwitch persistence extension
# Copyright (C) 2016 Petr Horacek <phoracek@redhat.com>
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free Software
# Foundation, either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the GNU General Public License along with
# this program. If not, see <http://www.gnu.org/licenses/>.
from subprocess import check_call, check_output
import json
import logging
import itertools


_OVSDB_TOOL = '/usr/bin/ovsdb-tool'
_OVS_VSCTL = '/usr/bin/ovs-vsctl'


def apply_persistence_config():
    logging.info('Starting OVS persistence update.')

    logging.info('Querying for non-persistent devices.')
    bridges, ports = _get_non_persistent_bridges_ports()
    logging.info(
        'Non-persistent bridges: {}, ports: {}.'.format(bridges, ports))

    if bridges or ports:
        logging.info('Removing non-persistent devices.')
        _remove_devices(bridges, ports)
        logging.info('Removal complete.')
    else:
        logging.info('Nothing to remove.')


def _get_non_persistent_bridges_ports():
    query = [
        'Open_vSwitch',
        _select_non_persistent_rows('Bridge'),
        _select_non_persistent_rows('Port')]
    non_persistent_rows = _call_ovsdb_tool(['query', json.dumps(query)])

    bridges = [row['name'] for row in non_persistent_rows[0]['rows']]
    ports = [row['name'] for row in non_persistent_rows[1]['rows']]

    return bridges, ports


def _select_non_persistent_rows(table_name):
    return {
        'table': table_name,
        'op': 'select',
        'columns': ['name'],
        'where': [
            ['other_config',
             'includes',
             ['map', [['persistent', 'false']]]]
        ]
    }


def _call_ovsdb_tool(args_list):
    logging.debug('Calling ovsdb-tool with: {}.'.format(args_list))
    output = check_output([_OVSDB_TOOL] + args_list, universal_newlines=True)
    logging.debug('ovsdb-tool returned: {}.'.format(output))
    return json.loads(output)


def _remove_devices(bridges, ports):
    del_brs = [['--if-exists', 'del-br', bridge, '--'] for bridge in bridges]
    del_ports = [['--if-exists', 'del-port', port, '--'] for port in ports]
    _call_ovs_vsctl(list(itertools.chain.from_iterable(del_brs + del_ports)))


def _call_ovs_vsctl(args_list):
    logging.debug('Calling ovs-vsctl with: {}.'.format(args_list))
    check_call([_OVS_VSCTL] + args_list)


if __name__ == '__main__':
    apply_persistence_config()
