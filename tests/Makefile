#!/usr/bin/make -f

# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to title 17 Section 105 of the
# United States Code this software is not subject to copyright
# protection and is in the public domain. NIST assumes no
# responsibility whatsoever for its use by other parties, and makes
# no guarantees, expressed or implied, about its quality,
# reliability, or any other characteristic.
#
# We would appreciate acknowledgement if the software is used.

SHELL = /bin/bash

PYTHON3 ?= $(shell which python3 2>/dev/null || which python3.5)

all:

check: \
  check-cfreds-macwd.done.log
	@echo Tests passed!

check-cfreds-macwd.done.log: \
  check-cfreds-macwd.py \
  cfreds-macwd.dfxml
	$(PYTHON3) check-cfreds-macwd.py cfreds-macwd.dfxml
	touch $@

check-rx_partition_fs_type_code_and_label.done.log: \
  ../disktype_to_dfxml.py \
  check-rx_partition_fs_type_code_and_label.py
	$(PYTHON3) check-rx_partition_fs_type_code_and_label.py
	touch $@

clean:
	@rm -f *.dfxml *.done.log *.err.log

../Objects.py:
	@echo "ERROR:Makefile:Objects.py is a broken link.  Please run 'git submodule init; git submodule update' in the top directory of this repository." >&2
	exit 72

%.dfxml: \
  %.txt \
  ../Objects.py \
  ../disktype_to_dfxml.py \
  check-rx_partition_fs_type_code_and_label.done.log
	$(PYTHON3) ../disktype_to_dfxml.py --debug $< 2> $@.err.log | xmllint --format - > _$@
	mv _$@ $@
