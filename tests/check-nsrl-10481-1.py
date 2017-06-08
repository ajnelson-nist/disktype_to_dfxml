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

assert dobj.volumes[0].partition_offset == 0
assert dobj.volumes[0].block_count == 322017

assert dobj.volumes[1].byte_runs[0].img_offset == 232292 * 2048
assert dobj.volumes[1].byte_runs[0].len == 2949120
