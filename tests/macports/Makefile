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
  check-nsrl-1-1.done.log \
  check-nsrl-100-1.done.log \
  check-nsrl-10298-2.done.log \
  check-nsrl-1035-1.done.log \
  check-nsrl-1036-1.done.log \
  check-nsrl-10728-1.done.log \
  check-nsrl-11957-2.done.log \
  check-nsrl-119647-1.done.log \
  check-nsrl-12186-1.done.log \
  check-nsrl-12230-1.done.log \
  check-nsrl-12441-3.done.log \
  check-nsrl-12579-1.done.log \
  check-nsrl-12636-1.done.log \
  check-nsrl-1267-4.done.log \
  check-nsrl-1289-1.done.log \
  check-nsrl-13204-1.done.log \
  check-nsrl-14480-1.done.log \
  check-nsrl-1489-1.done.log \
  check-nsrl-16033-1.done.log \
  check-nsrl-2332-1.done.log \
  check-nsrl-2334-1.done.log \
  check-nsrl-31529-1.done.log \
  check-nsrl-7316-1.done.log \
  check-nsrl-7476-1.done.log \
  check-nsrl-9248-1.done.log \
  check-nsrl-9297-1.done.log \
  check-nsrl-9297-10.done.log
	@echo Macports tests passed!

#TODO
check-nsrl-1-1.done.log: \
  nsrl-1-1.dfxml

#TODO
check-nsrl-100-1.done.log: \
  nsrl-100-1.dfxml

#TODO
check-nsrl-10298-2.done.log: \
  nsrl-10298-2.dfxml

#TODO
check-nsrl-1035-1.done.log: \
  nsrl-1035-1.dfxml

#TODO
check-nsrl-1036-1.done.log: \
  nsrl-1036-1.dfxml

#TODO
check-nsrl-10728-1.done.log: \
  nsrl-10728-1.dfxml

#TODO
check-nsrl-11957-2.done.log: \
  nsrl-11957-2.dfxml

#TODO
check-nsrl-119647-1.done.log: \
  nsrl-119647-1.dfxml

#TODO
check-nsrl-12186-1.done.log: \
  nsrl-12186-1.dfxml

#TODO
check-nsrl-12230-1.done.log: \
  nsrl-12230-1.dfxml

#TODO
check-nsrl-12441-3.done.log: \
  nsrl-12441-3.dfxml

#TODO
check-nsrl-12579-1.done.log: \
  nsrl-12579-1.dfxml

#TODO
check-nsrl-12636-1.done.log: \
  nsrl-12636-1.dfxml

#TODO
check-nsrl-1267-4.done.log: \
  nsrl-1267-4.dfxml

#TODO
check-nsrl-1289-1.done.log: \
  nsrl-1289-1.dfxml

#TODO
check-nsrl-13204-1.done.log: \
  nsrl-13204-1.dfxml

#TODO
check-nsrl-14480-1.done.log: \
  nsrl-14480-1.dfxml

#TODO
check-nsrl-1489-1.done.log: \
  nsrl-1489-1.dfxml

#TODO
check-nsrl-16033-1.done.log: \
  nsrl-16033-1.dfxml

#TODO
check-nsrl-2332-1.done.log: \
  nsrl-2332-1.dfxml

#TODO
check-nsrl-2334-1.done.log: \
  nsrl-2334-1.dfxml

#TODO
check-nsrl-31529-1.done.log: \
  nsrl-31529-1.dfxml

#TODO
check-nsrl-7316-1.done.log: \
  nsrl-7316-1.dfxml

#TODO
check-nsrl-7476-1.done.log: \
  nsrl-7476-1.dfxml

#TODO
check-nsrl-9248-1.done.log: \
  nsrl-9248-1.dfxml

#TODO
check-nsrl-9297-1.done.log: \
  nsrl-9297-1.dfxml

#TODO
check-nsrl-9297-10.done.log: \
  nsrl-9297-10.dfxml

clean:
	@rm -f *.dfxml *.done.log *.err.log
