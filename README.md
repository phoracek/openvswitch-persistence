# Open vSwitch persistence

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
