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

logging.basicConfig(level=logging.INFO)

import Objects

dobj = Objects.parse(sys.argv[1])

assert dobj.volumes[0].ftype_str == "ISO9660"
assert dobj.volumes[0].block_count == 96
assert dobj.volumes[0].block_size == 2048
assert dobj.volumes[0].byte_runs[0].img_offset == 0
assert dobj.volumes[0].byte_runs[0].len == 196608 #NOTE: The containing partition's size is 327680 bytes.

assert dobj.volumes[1].ftype_str == "UFS"
logging.info(dobj.volumes[1].block_count)
assert dobj.volumes[1].block_size == 512
assert dobj.volumes[1].byte_runs[0].img_offset == 640 * 512
assert dobj.volumes[1].byte_runs[0].len == 629800960

assert dobj.volumes[2].ftype_str == "UFS"
logging.info(dobj.volumes[2].block_count)
assert dobj.volumes[2].block_size == 512
assert dobj.volumes[2].byte_runs[0].img_offset == 1230720 * 512
assert dobj.volumes[2].byte_runs[0].len == 2412544

assert dobj.volumes[3].ftype_str == "UFS"
logging.info(dobj.volumes[3].block_count)
assert dobj.volumes[3].block_size == 512
assert dobj.volumes[3].byte_runs[0].img_offset == 1235840 * 512
assert dobj.volumes[3].byte_runs[0].len == 2621440

assert dobj.volumes[4].ftype_str == "UFS"
logging.info(dobj.volumes[4].block_count)
assert dobj.volumes[4].block_size == 512
assert dobj.volumes[4].byte_runs[0].img_offset == 1240960 * 512
assert dobj.volumes[4].byte_runs[0].len == 2621440

assert dobj.volumes[5].ftype_str == "UFS"
logging.info(dobj.volumes[5].block_count)
assert dobj.volumes[5].block_size == 512
assert dobj.volumes[5].byte_runs[0].img_offset == 1246080 * 512
assert dobj.volumes[5].byte_runs[0].len == 2621440
