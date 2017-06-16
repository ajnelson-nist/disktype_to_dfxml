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

%.dfxml: \
  %.txt \
  ../../Objects.py \
  ../../disktype_to_dfxml.py
	$(PYTHON3) ../../disktype_to_dfxml.py --debug $< 2> $@.err.log | xmllint --format - > _$@
	mv _$@ $@

check: \
  check-2009-m57-patents-redacted-charlie-work-usb-2009-12-11.done.log \
  check-2009-m57-patents-redacted-jo-favorites-usb-2009-12-11.done.log \
  check-2009-m57-patents-redacted-terry-2009-12-11-002.done.log \
  check-2009-nps-ubnist1-gen0.done.log \
  check-2010-dftt-test14-iso-dirtree2.done.log \
  check-2011-nps-2tb.done.log \
  check-2012-ngdc-tracy-phone-2012-07-03-initial.done.log \
  check-2014-nps-xbox360-drive2-time0.done.log \
  check-archivematica-sampledata-BagTransfer.done.log \
  check-cfreds-macwd.done.log \
  check-cfreds_2015_data_leakage_rm3.done.log \
  check-nsrl-10002-1.done.log \
  check-nsrl-10003-2.done.log \
  check-nsrl-10005-1.done.log \
  check-nsrl-10051-1.done.log \
  check-nsrl-10198-1.done.log \
  check-nsrl-1025-2.done.log \
  check-nsrl-1035-1.done.log \
  check-nsrl-1035-2.done.log \
  check-nsrl-1036-1.done.log \
  check-nsrl-10453-1.done.log \
  check-nsrl-10478-1.done.log \
  check-nsrl-10481-1.done.log \
  check-nsrl-10483-1.done.log \
  check-nsrl-10485-1.done.log \
  check-nsrl-1051-1.done.log \
  check-nsrl-10515-1.done.log \
  check-nsrl-10601-1.done.log \
  check-nsrl-10607-1.done.log \
  check-nsrl-10618-1.done.log \
  check-nsrl-10619-1.done.log \
  check-nsrl-10714-1.done.log \
  check-nsrl-10728-1.done.log \
  check-nsrl-10729-1.done.log \
  check-nsrl-10825-1.done.log \
  check-nsrl-10970-1.done.log \
  check-nsrl-11014-1.done.log \
  check-nsrl-11130-1.done.log \
  check-nsrl-11315-1.done.log \
  check-nsrl-11379-1.done.log \
  check-nsrl-16618-1.done.log \
  check-nsrl-31595-1.done.log \
  check-nsrl-5304-1.done.log \
  check-nsrl-9992-1.done.log
	@echo Ubuntu 16.04 tests passed!

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

#TODO
check-archivematica-sampledata-BagTransfer.done.log: \
  archivematica-sampledata-BagTransfer.dfxml

check-cfreds-macwd.done.log: \
  check-cfreds-macwd.py \
  cfreds-macwd.dfxml
	$(PYTHON3) check-cfreds-macwd.py cfreds-macwd.dfxml
	touch $@

check-cfreds_2015_data_leakage_rm3.done.log: \
  cfreds_2015_data_leakage_rm3.dfxml
	test 1 -eq $$(grep ftype_str $< | wc -l)

check-nsrl-10002-1.done.log: \
  nsrl-10002-1.dfxml \
  check-nsrl-10002-1.py
	$(PYTHON3) check-nsrl-10002-1.py nsrl-10002-1.dfxml
	touch $@

#TODO
check-nsrl-10003-2.done.log: \
  nsrl-10003-2.dfxml

#TODO
check-nsrl-10005-1.done.log: \
  nsrl-10005-1.dfxml

#TODO
check-nsrl-10051-1.done.log: \
  nsrl-10051-1.dfxml

#TODO
check-nsrl-1025-2.done.log: \
  nsrl-1025-2.dfxml

#TODO
check-nsrl-1035-1.done.log: \
  nsrl-1035-1.dfxml

#TODO
check-nsrl-1035-2.done.log: \
  nsrl-1035-2.dfxml

#TODO
check-nsrl-1036-1.done.log: \
  nsrl-1036-1.dfxml

#TODO
check-nsrl-10453-1.done.log: \
  nsrl-10453-1.dfxml

#TODO
check-nsrl-10478-1.done.log: \
  nsrl-10478-1.dfxml

check-nsrl-10481-1.done.log: \
  nsrl-10481-1.dfxml \
  check-nsrl-10481-1.py
	$(PYTHON3) check-nsrl-10481-1.py nsrl-10481-1.dfxml
	touch $@

#TODO
check-nsrl-10483-1.done.log: \
  nsrl-10483-1.dfxml

#TODO
check-nsrl-10485-1.done.log: \
  nsrl-10485-1.dfxml

#TODO
check-nsrl-1051-1.done.log: \
  nsrl-1051-1.dfxml

#TODO
check-nsrl-10515-1.done.log: \
  nsrl-10515-1.dfxml

#TODO
check-nsrl-10601-1.done.log: \
  nsrl-10601-1.dfxml

#TODO
check-nsrl-10607-1.done.log: \
  nsrl-10607-1.dfxml

#TODO
check-nsrl-10618-1.done.log: \
  nsrl-10618-1.dfxml

#TODO
check-nsrl-10619-1.done.log: \
  nsrl-10619-1.dfxml

#TODO
check-nsrl-10198-1.done.log: \
  nsrl-10198-1.dfxml

#TODO
check-nsrl-10714-1.done.log: \
  nsrl-10714-1.dfxml

#TODO
check-nsrl-10728-1.done.log: \
  nsrl-10728-1.dfxml

#TODO
check-nsrl-10729-1.done.log: \
  nsrl-10729-1.dfxml

#TODO
check-nsrl-10825-1.done.log: \
  nsrl-10825-1.dfxml

#TODO
check-nsrl-10970-1.done.log: \
  nsrl-10970-1.dfxml

#TODO
check-nsrl-11014-1.done.log: \
  nsrl-11014-1.dfxml

#TODO
check-nsrl-11130-1.done.log: \
  nsrl-11130-1.dfxml

#TODO
check-nsrl-11315-1.done.log: \
  nsrl-11315-1.dfxml

check-nsrl-11379-1.done.log: \
  nsrl-11379-1.dfxml
	test 1 -eq $$(grep ftype_str $< | wc -l)

check-nsrl-16618-1.done.log: \
  nsrl-16618-1.dfxml \
  check-nsrl-16618-1.py
	$(PYTHON3) check-nsrl-16618-1.py nsrl-16618-1.dfxml
	touch $@

check-nsrl-31595-1.done.log: \
  nsrl-31595-1.dfxml
	test 2 -eq $$(grep ftype_str $< | wc -l)
	test 2 -eq $$(grep partition_offset $< | wc -l)

check-nsrl-5304-1.done.log: \
  nsrl-5304-1.dfxml
	test 1 -eq $$(egrep '^  <' $< | grep pstype_str | wc -l)
	test 2 -eq $$(grep ftype_str $< | wc -l)
	test 1 -eq $$(grep ftype_str $< | grep '>HFS<' | wc -l)
	test 1 -eq $$(grep ftype_str $< | grep ISO9660 | wc -l)

check-nsrl-9992-1.done.log: \
  nsrl-9992-1.dfxml
	test 1 -eq $$(grep ftype_str $< | grep ISO9660 | wc -l)

clean:
	@rm -f *.dfxml *.done.log *.err.log
