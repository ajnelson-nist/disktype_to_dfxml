#!/usr/bin/env python3

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

import sys
import logging
import os
import copy

_logger = logging.getLogger(os.path.basename(__file__))
logging.basicConfig(level=logging.DEBUG)

import Objects

dobj = Objects.parse(sys.argv[1])

assert dobj.volumes[0].ftype_str == "HFS"
assert dobj.volumes[0].block_count == 9194
assert dobj.volumes[0].block_size == 72 * 2**10
assert dobj.volumes[0].byte_runs[0].img_offset == 495616
assert dobj.volumes[0].byte_runs[0].len == 73728 * 9194

#The wrapped volume needs to be extracted with a little API work.  Objects.py doesn't know to emit the volume when it is an extension element.
assert len(dobj.volumes) == 1 #2

wrapped_vobj = None
for el in dobj.volumes[0].externals:
    _logger.debug("Checking element with name %r." % el.tag)
    if el.tag != "{http://www.forensicswiki.org/wiki/Category:Digital_Forensics_XML#extensions}wrapped_hfsplus_volume":
        continue

    #Copy the element, because populate_from_Element enforces tag name.
    cel = copy.deepcopy(el)
    cel.tag = "volume"

    wrapped_vobj = Objects.VolumeObject()
    wrapped_vobj.populate_from_Element(cel)
    break
assert not wrapped_vobj is None
assert wrapped_vobj.ftype_str == "HFS Plus"
assert wrapped_vobj.block_count == 165402
assert wrapped_vobj.block_size == 4096
assert wrapped_vobj.byte_runs[0].len == 4096 * 165402

#From manual inspection of this disk image:
#  The img_offset of the embedded HFS+ file system is 93 4KiB sectors after the start of Partition 9.
#  Disktype does not emit that detail, but Fiwalk does find the embedded file system if told to walk the partition.
#  Since the offset can't be computed from Disktype's current output, skip this test.
#assert wrapped_vobj.byte_runs[0].img_offset == 876544
