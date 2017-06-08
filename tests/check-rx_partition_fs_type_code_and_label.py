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

"""
This script spot-checks that some strings encountered in sample data match against expected regular expressions.
"""

import logging
import os
import sys

logging.basicConfig(level=logging.DEBUG)
_logger = logging.getLogger(os.path.basename(__file__))

sys.path.append("..")
import disktype_to_dfxml

maybe_match = disktype_to_dfxml.rx_partition_ptype_and_ptype_str.search(b"    Type 7 (4.2BSD fast file system)".strip())
assert not maybe_match is None
_logger.debug(maybe_match.group("ptype"))
assert maybe_match.group("ptype") == b"7"

maybe_match = disktype_to_dfxml.rx_partition_ptype_and_ptype_str.search(b"  Type 0x07 (HPFS/NTFS)".strip())
assert not maybe_match is None
_logger.debug(maybe_match.group("ptype"))
assert maybe_match.group("ptype") == b"0x07"

maybe_match = disktype_to_dfxml.rx_partition_ptype_str_ftype_str_and_guid.search(b"  Type EFI System (FAT) (GUID 28732AC1-1FF8-D211-BA4B-00A0C93EC93B)".strip())
assert not maybe_match is None
_logger.debug(maybe_match.groups())
assert not maybe_match.group("ftype_str") is None
assert maybe_match.group("ftype_str") == b"FAT"

maybe_match = disktype_to_dfxml.rx_partition_ptype_str_and_guid.search(b"  Type Basic Data (GUID A2A0D0EB-E5B9-3344-87C0-68B6B72699C7)".strip())
assert not maybe_match is None
_logger.debug(maybe_match.groups())

maybe_match = disktype_to_dfxml.rx_publisher.search(b'  Publisher   "MICROSOFT CORPORATION"\n'.strip())
assert not maybe_match is None

maybe_match = disktype_to_dfxml.rx_partition_meta_size_summary.search(b'Partition 9: 8.688 MiB (9109504 bytes, 17792 sectors from 183792)\n'.strip())
assert not maybe_match is None

maybe_match = disktype_to_dfxml.rx_partition_meta_no_size_summary.search(b'Partition 4: 0 bytes (0 sectors from 0)\n'.strip())
assert not maybe_match is None

maybe_match = disktype_to_dfxml.rx_boot_loader.search(b'      ISOLINUX boot loader\n'.strip())
assert not maybe_match is None
