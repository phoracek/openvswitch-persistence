FROM fedora
MAINTAINER Petr Horacek <phoracek@redhat.com>

RUN dnf -y install openvswitch which && dnf clean all; \
systemctl enable openvswitch.service

RUN pip install pep8 pyflakes pytest

RUN systemctl mask systemd-remount-fs.service dev-hugepages.mount \
    sys-fs-fuse-connections.mount systemd-logind.service getty.target \
    console-getty.service dnf-makecache.service
RUN cp /usr/lib/systemd/system/dbus.service /etc/systemd/system/; \
    sed -i 's/OOMScoreAdjust=-900//' /etc/systemd/system/dbus.service

VOLUME ["/run", "/tmp"]

ENV container=docker

WORKDIR /root/openvswitch-persistence

CMD ["/usr/sbin/init"]
