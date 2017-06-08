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
  check-cfreds-macwd.done.log \
  check-2009-m57-patents-redacted-charlie-work-usb-2009-12-11.done.log \
  check-2009-m57-patents-redacted-jo-favorites-usb-2009-12-11.done.log \
  check-2009-m57-patents-redacted-terry-2009-12-11-002.done.log \
  check-2009-nps-ubnist1-gen0.done.log \
  check-2010-dftt-test14-iso-dirtree2.done.log \
  check-2011-nps-2tb.done.log \
  check-2012-ngdc-tracy-phone-2012-07-03-initial.done.log \
  check-2014-nps-xbox360-drive2-time0.done.log \
  check-cfreds_2015_data_leakage_rm3.done.log
	@echo Tests passed!

# The pstype_str egrep line looks for pstype_str attached to the root element only.
check-2009-m57-patents-redacted-charlie-work-usb-2009-12-11.done.log: \
  2009-m57-patents-redacted-charlie-work-usb-2009-12-11.dfxml
	test 1 -eq $$(grep ftype_str $< | wc -l)
	test 1 -eq $$(egrep '^  <' $< | grep pstype_str | wc -l)

check-2009-m57-patents-redacted-jo-favorites-usb-2009-12-11.done.log: \
  2009-m57-patents-redacted-jo-favorites-usb-2009-12-11.dfxml
	test 1 -eq $$(grep ftype_str $< | wc -l)
	test 1 -eq $$(egrep '^  <' $< | grep pstype_str | wc -l)

check-2009-m57-patents-redacted-terry-2009-12-11-002.done.log: \
  2009-m57-patents-redacted-terry-2009-12-11-002.dfxml
	test 2 -eq $$(grep ftype_str $< | wc -l)
	test 2 -eq $$(egrep '^  <' $< | grep pstype_str | wc -l)

check-2009-nps-ubnist1-gen0.done.log: \
  2009-nps-ubnist1-gen0.dfxml
	test 1 -eq $$(grep ftype_str $< | wc -l)

check-2010-dftt-test14-iso-dirtree2.done.log: \
  2010-dftt-test14-iso-dirtree2.dfxml
	test 1 -eq $$(grep ftype_str $< | grep ISO9660 | wc -l)

check-2011-nps-2tb.done.log: \
  2011-nps-2tb.dfxml
	test 1 -eq $$(grep ftype_str $< | wc -l)

#This is one of those cases where it would be a little helpful to have a partition denotation for the GPT guard partition.
check-2012-ngdc-tracy-phone-2012-07-03-initial.done.log: \
  2012-ngdc-tracy-phone-2012-07-03-initial.dfxml
	test 1 -eq $$(grep pstype_str $< | wc -l)

#No tests here - just want to make sure the XML builds.  Disktype doesn't recognize the XBox 360 partitioning system.
check-2014-nps-xbox360-drive2-time0.done.log: \
  2014-nps-xbox360-drive2-time0.dfxml
	touch $@

check-cfreds-macwd.done.log: \
  check-cfreds-macwd.py \
  cfreds-macwd.dfxml
	$(PYTHON3) check-cfreds-macwd.py cfreds-macwd.dfxml
	touch $@

check-cfreds_2015_data_leakage_rm3.done.log: \
  cfreds_2015_data_leakage_rm3.dfxml
	test 1 -eq $$(grep ftype_str $< | wc -l)

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
