# Open vSwitch persistence

[![Build Status](https://travis-ci.org/phoracek/openvswitch-persistence.svg?branch=master)](https://travis-ci.org/phoracek/openvswitch-persistence)

Extension for Open vSwitch allowing users to mark Bridge/Port as
non-persistent. Such device will be removed on openvswitch.service restart.


## Instalation

```
make install
systemctl enable
```


## Usage

```
ovs-vsctl set Bridge other_config:persistent=false
```


## Example

```
# ovs-vsctl \
    add-br br0 -- \
	add-port br0 port0 -- \
	set Port port0 other_config:persistent=false -- \
	add-br br1 -- \
	set Bridge br1 other_config:persistent=false -- \
	add-port br1 port1

# ovs-vsctl show
6afd7ed7-6938-42ec-b650-effd775c5c9c
    Bridge "br1"
        Port "port1"
            Interface "port1"
        Port "br1"
            Interface "br1"
                type: internal
    Bridge "br0"
        Port "br0"
            Interface "br0"
                type: internal
        Port "port0"
            Interface "port0"
    ovs_version: "2.5.0"

# systemctl restart openvswitch

# ovs-vsctl show
6afd7ed7-6938-42ec-b650-effd775c5c9c
	Bridge "br0"
		Port "br0"
			Interface "br0"
		type: internal
	ovs_version: "2.5.0"
```
