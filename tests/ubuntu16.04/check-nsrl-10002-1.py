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
import Objects

dobj = Objects.parse(sys.argv[1])

assert len(dobj.volumes) == 2

assert dobj.volumes[0].ftype_str == "HFS"
assert dobj.volumes[1].ftype_str == "HFS Plus"

assert dobj.volumes[0].block_count == 9194
assert dobj.volumes[1].block_count == 165402

assert dobj.volumes[0].block_size == 72 * 2**10
assert dobj.volumes[1].block_size == 4096

assert dobj.volumes[0].byte_runs[0].img_offset == 495616
assert dobj.volumes[1].byte_runs[0].img_offset == 495616

assert dobj.volumes[0].byte_runs[0].len == 73728 * 9194
assert dobj.volumes[1].byte_runs[0].len == 4096 * 165402
