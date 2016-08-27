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
DESTDIR ?=
DATA_PREFIX ?= /usr/share
LIB_PREFIX ?= /usr/lib

# Python binary which should be used to run tests.
PYTHON ?= $(shell which python)

# Whether test container should be removed after successful test or not.
REMOVE_CONTAINER_AFTER_SUCCESS ?= 1

openvswitch-persistence: service

.PHONY: service
service:
	@echo 'Replacing placeholder variables in service file...'
	sed \
		-e "s%@DESTDIR@%$(DESTDIR)%" \
		-e "s%@DATA_PREFIX@%$(DATA_PREFIX)%" \
		< systemd/openvswitch-persistence.service.in \
		> systemd/openvswitch-persistence.service

.PHONY: install
install: service
	@echo 'Installing executable...'
	install -m 0744 -d \
		$(DESTDIR)$(DATA_PREFIX)/openvswitch-persistence
	install -m 0744 \
		src/apply.py \
		$(DESTDIR)$(DATA_PREFIX)/openvswitch-persistence
	@echo 'Installing service...'
	install -m 0644 \
		systemd/openvswitch-persistence.service \
		$(DESTDIR)$(LIB_PREFIX)/systemd/system
	@echo 'Installation complete.'

.PHONY: uninstall
uninstall:
	@echo 'Removing executable and its directory...'
	rm -rf \
		$(DESTDIR)$(DATA_PREFIX)/openvswitch-persistence
	@echo 'Removing service...'
	rm -rf \
		$(DESTDIR)$(LIB_PREFIX)/systemd/system/openvswitch-persistence.service

.PHONY: clean
clean:
	git clean -d -x --force

.PHONY: pep8
pep8:
	$(PYTHON) -m pep8 src/*.py tests/*.py
	@echo 'PEP8 test passed.'

.PHONY: pyflakes
pyflakes:
	$(PYTHON) -m pyflakes src/*.py tests/*.py
	@echo 'Pyflakes test passed.'

.PHONY: check
check: pep8 pyflakes

.PHONY: test
test:
	$(PYTHON) -m pytest tests/*.py

.PHONY: docker-image
docker-image:
	docker build --tag fedora/openvswitch-persistence tests

.PHONY: test-in-container
test-in-container: docker-image
	$(eval \
		cid := $(shell \
			docker run --tty --detach --cap-add NET_ADMIN \
			--volume /sys/fs/cgroup:/sys/fs/cgroup \
			fedora/openvswitch-persistence))
	docker cp . $(cid):/root/openvswitch-persistence
	docker exec $(cid) make check
	docker exec $(cid) make install
	docker exec $(cid) systemctl enable openvswitch-persistence
	docker exec $(cid) make test
ifeq ($(REMOVE_CONTAINER_AFTER_SUCCESS), 1)
	@echo 'Removing container.'
	docker rm --force $(cid)
endif
