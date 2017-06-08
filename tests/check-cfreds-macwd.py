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

assert dobj.volumes[0].ftype_str == "HFS Plus"
assert dobj.volumes[1].ftype_str == "HFS Plus"
assert dobj.volumes[2].ftype_str == "HFS Plus"
assert dobj.volumes[3].ftype_str == "HFS"
assert dobj.volumes[4].ftype_str == "HFS Plus"
assert dobj.volumes[5].ftype_str == "UFS"

assert dobj.volumes[0].block_size == 4096
assert dobj.volumes[1].block_size == 4096
assert dobj.volumes[2].block_size == 4096
assert dobj.volumes[3].block_size == 512
assert dobj.volumes[4].block_size == 4096
assert dobj.volumes[5].block_size == 512

assert dobj.volumes[0].byte_runs[0].img_offset == 512 * 64
assert dobj.volumes[1].byte_runs[0].img_offset == 512 * 33016
assert dobj.volumes[2].byte_runs[0].img_offset == 512 * 80872
assert dobj.volumes[3].byte_runs[0].img_offset == 512 * 131080
assert dobj.volumes[4].byte_runs[0].img_offset == 512 * 166384
assert dobj.volumes[5].byte_runs[0].img_offset == 512 * 183792

assert dobj.volumes[0].byte_runs[0].len == 16871424
assert dobj.volumes[1].byte_runs[0].len == 16871424
assert dobj.volumes[2].byte_runs[0].len == 17674240
assert dobj.volumes[3].byte_runs[0].len == 512 * 35290
assert dobj.volumes[3].block_count == 35290
assert dobj.volumes[4].byte_runs[0].len == 8912896
assert dobj.volumes[4].block_count == 2176
assert dobj.volumes[5].byte_runs[0].len == 9109504
assert dobj.volumes[5].block_count == 17792
