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

__version__ = "0.2.0"

import subprocess
import re
import enum
import os
import logging
import sys
import xml.etree.ElementTree as ET
import copy

_logger = logging.getLogger(os.path.basename(__file__))

import Objects

XMLNS_DFXML_EXT = Objects.dfxml.XMLNS_DFXML + "#extensions"

block_units = {
  "bytes": 2**0,
  "KiB"  : 2**10,
  "MiB"  : 2**20,
  "GiB"  : 2**30
}

class DiskImageObject(object):
    def __init__(self):
        self.byte_runs = Objects.ByteRuns()
        self.partition_systems = []
        self.sector_size = None
        self.volumes = []

    def __str__(self):
        parts = []
        for prop in [
          "byte_runs",
          "partition_systems",
          "sector_size",
          "volumes"
        ]:
            val = getattr(self, prop)
            if val:
                parts.append("%s=%s" % (prop, val))
        return "DiskImageObject(" + ", ".join(parts) + ")"

    def append(self, obj):
        if isinstance(obj, PartitionSystemObject):
            self.partition_systems.append(obj)
        elif isinstance(obj, Objects.VolumeObject):
            self.volumes.append(obj)
        else:
            raise ValueError("Unexpected object type passed to DiskImageObject.append(): %r." % type(obj))

class PartitionSystemObject(object):
    def __init__(self):
        self.block_size = None
        self.byte_runs = Objects.ByteRuns()
        self.guid = None
        self.partitions = []
        self.pstype_str = None

    def __str__(self):
        parts = []
        for prop in [
          "block_size",
          "byte_runs",
          "guid",
          "partitions",
          "pstype_str"
        ]:
            val = getattr(self, prop)
            if val:
                parts.append("%s=%s" % (prop, val))
        return "PartitionSystemObject(" + ", ".join(parts) + ")"

    def append(self, obj):
        if isinstance(obj, PartitionObject):
            self.partitions.append(obj)
        else:
            raise ValueError("Unexpected object type passed to PartitionSystemObject.append(): %r." % type(obj))

class PartitionObject(object):
    def __init__(self):
        self.block_count = None
        self.block_size = None
        self.byte_runs = Objects.ByteRuns()
        self.ftype_str = None
        self.guid = None
        self.partition_system_offset = None #Unit: bytes.  Offset within partition system.  Could also be byte_run/@ps_offset, if that were defined in the Objects.ByteRun class.
        self.partition_systems = []
        self.ptype = None
        self.ptype_str = None
        self.volumes = []

    def __str__(self):
        parts = []
        for prop in [
          "block_count",
          "block_size",
          "byte_runs",
          "ftype_str",
          "guid",
          "partition_system_offset",
          "partition_systems",
          "ptype",
          "ptype_str",
          "volumes"
        ]:
            val = getattr(self, prop)
            if val:
                parts.append("%s=%s" % (prop, val))
        return "PartitionObject(" + ", ".join(parts) + ")"

    def append(self, obj):
        if isinstance(obj, PartitionSystemObject):
            self.partition_systems.append(obj)
        elif isinstance(obj, Objects.VolumeObject):
            self.volumes.append(obj)
        else:
            raise ValueError("Unexpected object type passed to PartitionObject.append(): %r." % type(obj))

class ParseState(enum.Enum):
    _INPUT_START                           =   0
    _INPUT_END                             = 999

    #Misc. and multi-category states
    BLANK_MEDIUM                           =   1
    SECTOR_SIZE                            =   2
    SOLARIS_SPARC_DISKLABEL                =   3
    TAR_ARCHIVE                            =   4

    _DISK_START                            = 100
    CPIO_ARCHIVE                           = 101
    DISK_META                              = 102
    INPUT_FILE                             = 103
    NO_TYPE_AND_CREATOR_CODE               = 104
    VALIDATION_ENTRY_MISSING               = 105
    _DISK_END                              = 199

    _PARTITION_SYSTEM_START                = 200
    DISK_GUID                              = 201
    DISK_SIZE                              = 202
    PARTITION_MAP                          = 203
    _PARTITION_SYSTEM_END                  = 299

    _PARTITION_START                       = 300
    BOOTABLE_FLOPPY_IMAGE                  = 301
    BOOTABLE_HARD_DISK_IMAGE               = 302
    BOOTABLE_NONEMULATED_IMAGE             = 303
    FILE_SYSTEM_INCLUDES                   = 304
    PARTITION_BLANK_CHECK                  = 305
    PARTITION_GUID                         = 306
    PARTITION_INCLUDES                     = 307
    PARTITION_META                         = 308
    PARTITION_NAME                         = 309
    PARTITION_PTYPE_INT                    = 310
    PARTITION_PTYPE_STR                    = 311
    PARTITION_PTYPE_AND_PTYPE_STR          = 312
    PARTITION_PTYPE_STR_AND_GUID           = 313
    PARTITION_PTYPE_STR_FTYPE_STR_AND_GUID = 314
    PARTITION_UNUSED                       = 315
    SIGNATURE_MISSING                      = 316
    _PARTITION_END                         = 399

    _FILE_SYSTEM_START                     = 400
    ADDITIONAL_PRIMARY_VOLUME_DESCRIPTOR   = 401
    APPLICATION                            = 402
    BOOT_LOADER                            = 403
    BOOT_RECORD                            = 404
    BSD_DISKLABEL                          = 405
    DATA_SIZE                              = 406
    DESCRIPTOR_TYPE                        = 407
    FILE_SYSTEM_UUID                       = 408
    FS_TYPE_STR                            = 409
    HFS_WRAPPER                            = 410
    ISO9660_EXTENSION                      = 411
    LAST_MOUNTED                           = 412
    PLATFORM_SYSTEM_TYPE                   = 413
    PREPARER                               = 414
    PUBLISHER                              = 415
    UDF_RECOGNITION_SEQUENCE_MISSINGLOC    = 416
    UDF_VERSION                            = 417
    VOLUME_NAME                            = 418
    VOLUME_SIZE                            = 419
    _FILE_SYSTEM_END                       = 499

    #El Torito state tracking is to ease indentation-based interpretations.
    _EL_TORITO_START                       = 500
    _EL_TORITO_END                         = 599

    _COMPRESSION_START                     = 600
    GZIP                                   = 601
    _COMPRESSION_END                       = 699

state_transitions = {
  ParseState._COMPRESSION_END: {
    ParseState._DISK_END,
  },
  ParseState._COMPRESSION_START: {
    ParseState.GZIP,
  },
  ParseState._DISK_END: {
    ParseState._DISK_START,
    ParseState._EL_TORITO_END,
    ParseState._INPUT_END,
  },
  ParseState._DISK_START: {
    ParseState.BOOTABLE_FLOPPY_IMAGE,
    ParseState.BOOTABLE_HARD_DISK_IMAGE,
    ParseState.BOOTABLE_NONEMULATED_IMAGE,
    ParseState.INPUT_FILE
  },
  ParseState._EL_TORITO_END: {
    ParseState._FILE_SYSTEM_END,
    ParseState.ADDITIONAL_PRIMARY_VOLUME_DESCRIPTOR,
    ParseState.ISO9660_EXTENSION
  },
  ParseState._EL_TORITO_START: {
    ParseState.BOOT_RECORD,
  },
  ParseState._FILE_SYSTEM_END: {
    ParseState._DISK_END,
    ParseState._FILE_SYSTEM_START,
    ParseState._PARTITION_END,
    ParseState._PARTITION_SYSTEM_START,
    ParseState.HFS_WRAPPER,
    ParseState.ISO9660_EXTENSION
  },
  ParseState._FILE_SYSTEM_START: {
    ParseState.FS_TYPE_STR
  },
  ParseState._INPUT_END: set(),
  ParseState._INPUT_START: {
    ParseState._DISK_START
  },
  ParseState._PARTITION_END: {
    ParseState._PARTITION_START,
    ParseState._PARTITION_SYSTEM_END
  },
  ParseState._PARTITION_START: {
    ParseState.PARTITION_META,
    ParseState.PARTITION_UNUSED
  },
  ParseState._PARTITION_SYSTEM_END: {
    ParseState._DISK_END,
    ParseState._FILE_SYSTEM_START,
    ParseState._PARTITION_END,
    ParseState._PARTITION_START,
    ParseState._PARTITION_SYSTEM_START,
    ParseState.UDF_RECOGNITION_SEQUENCE_MISSINGLOC
  },
  ParseState._PARTITION_SYSTEM_START: {
    ParseState.BSD_DISKLABEL,
    ParseState.PARTITION_MAP,
    ParseState.SOLARIS_SPARC_DISKLABEL
  },
  ParseState.ADDITIONAL_PRIMARY_VOLUME_DESCRIPTOR: {
    ParseState._FILE_SYSTEM_END,
    ParseState.ADDITIONAL_PRIMARY_VOLUME_DESCRIPTOR,
    ParseState.ISO9660_EXTENSION
  },
  ParseState.APPLICATION: {
    ParseState.DATA_SIZE
  },
  ParseState.BLANK_MEDIUM: {
    ParseState._DISK_END,
    ParseState._PARTITION_END
  },
  ParseState.BOOT_LOADER: {
    ParseState._DISK_END,
    ParseState._FILE_SYSTEM_END,
    ParseState._FILE_SYSTEM_START,
    ParseState._PARTITION_SYSTEM_START,
    ParseState.BOOT_LOADER
  },
  ParseState.BOOT_RECORD: {
    ParseState._DISK_START,
    ParseState.BOOTABLE_HARD_DISK_IMAGE,
    ParseState.BOOTABLE_NONEMULATED_IMAGE,
    ParseState.VALIDATION_ENTRY_MISSING
  },
  ParseState.BOOTABLE_FLOPPY_IMAGE: {
    ParseState.PLATFORM_SYSTEM_TYPE
  },
  ParseState.BOOTABLE_HARD_DISK_IMAGE: {
    ParseState.PLATFORM_SYSTEM_TYPE
  },
  ParseState.BOOTABLE_NONEMULATED_IMAGE: {
    ParseState.PLATFORM_SYSTEM_TYPE
  },
  ParseState.BSD_DISKLABEL: {
    ParseState._PARTITION_START
  },
  ParseState.CPIO_ARCHIVE: {
    ParseState._DISK_END
  },
  ParseState.DATA_SIZE: {
    ParseState._EL_TORITO_START,
    ParseState._FILE_SYSTEM_END,
    ParseState.ADDITIONAL_PRIMARY_VOLUME_DESCRIPTOR,
    ParseState.DESCRIPTOR_TYPE,
    ParseState.ISO9660_EXTENSION
  },
  ParseState.DESCRIPTOR_TYPE: {
    ParseState._FILE_SYSTEM_END
  },
  ParseState.DISK_GUID: {
    ParseState._PARTITION_START
  },
  ParseState.DISK_META: {
    ParseState._DISK_END,
    ParseState._FILE_SYSTEM_START,
    ParseState._PARTITION_SYSTEM_START,
    ParseState.BLANK_MEDIUM,
    ParseState.BOOT_LOADER,
    ParseState.CPIO_ARCHIVE,
    ParseState.NO_TYPE_AND_CREATOR_CODE,
    ParseState.TAR_ARCHIVE
  },
  ParseState.DISK_SIZE: {
    ParseState.DISK_GUID
  },
  ParseState.FILE_SYSTEM_UUID: {
    ParseState.VOLUME_SIZE
  },
  ParseState.FILE_SYSTEM_INCLUDES: {
    ParseState._FILE_SYSTEM_START
  },
  ParseState.FS_TYPE_STR: {
    ParseState._FILE_SYSTEM_END,
    ParseState.FILE_SYSTEM_UUID,
    ParseState.LAST_MOUNTED,
    ParseState.SECTOR_SIZE,
    ParseState.VOLUME_NAME,
    ParseState.VOLUME_SIZE
  },
  ParseState.GZIP: {
    ParseState.TAR_ARCHIVE
  },
  ParseState.INPUT_FILE: {
    ParseState.DISK_META
  },
  ParseState.HFS_WRAPPER: {
    ParseState._FILE_SYSTEM_START
  },
  ParseState.ISO9660_EXTENSION: {
    ParseState._DISK_END,
    ParseState._FILE_SYSTEM_END,
    ParseState._FILE_SYSTEM_START,
    ParseState.ISO9660_EXTENSION
  },
  ParseState.LAST_MOUNTED: {
    ParseState._FILE_SYSTEM_END,
    ParseState.PARTITION_META,
    ParseState.VOLUME_NAME
  },
  ParseState.NO_TYPE_AND_CREATOR_CODE: {
    ParseState._DISK_END
  },
  ParseState.PARTITION_BLANK_CHECK: {
    ParseState._PARTITION_END
  },
  ParseState.PARTITION_GUID: {
    ParseState._FILE_SYSTEM_START,
    ParseState._PARTITION_END
  },
  ParseState.PARTITION_INCLUDES: {
    ParseState._FILE_SYSTEM_START
  },
  ParseState.PARTITION_MAP: {
    ParseState._PARTITION_START,
    ParseState.DISK_SIZE,
    ParseState.PARTITION_META
  },
  ParseState.PARTITION_META: {
    ParseState.PARTITION_PTYPE_AND_PTYPE_STR,
    ParseState.PARTITION_PTYPE_INT,
    ParseState.PARTITION_PTYPE_STR,
    ParseState.PARTITION_PTYPE_STR_AND_GUID,
    ParseState.PARTITION_PTYPE_STR_FTYPE_STR_AND_GUID
  },
  ParseState.PARTITION_NAME: {
    ParseState.PARTITION_GUID
  },
  ParseState.PARTITION_UNUSED: {
    ParseState._PARTITION_END
  },
  ParseState.PLATFORM_SYSTEM_TYPE: {
    ParseState._DISK_END,
    ParseState._FILE_SYSTEM_END,
    ParseState._FILE_SYSTEM_START,
    ParseState._PARTITION_SYSTEM_START,
    ParseState.BOOT_LOADER
  },
  ParseState.PARTITION_PTYPE_AND_PTYPE_STR: {
    ParseState._FILE_SYSTEM_START,
    ParseState._PARTITION_END,
    ParseState.FILE_SYSTEM_INCLUDES,
    ParseState.SIGNATURE_MISSING
  },
  ParseState.PARTITION_PTYPE_INT: {
    ParseState._FILE_SYSTEM_START,
    ParseState._PARTITION_END,
    ParseState._PARTITION_SYSTEM_START,
    ParseState.BLANK_MEDIUM,
    ParseState.PARTITION_BLANK_CHECK,
    ParseState.PARTITION_INCLUDES,
    ParseState.PARTITION_META
  },
  ParseState.PARTITION_PTYPE_STR: {
    ParseState._FILE_SYSTEM_START,
    ParseState._PARTITION_END,
    ParseState._PARTITION_SYSTEM_START,
    ParseState.BLANK_MEDIUM,
    ParseState.PARTITION_BLANK_CHECK,
    ParseState.PARTITION_META
  },
  ParseState.PARTITION_PTYPE_STR_AND_GUID: {
    ParseState.PARTITION_NAME
  },
  ParseState.PARTITION_PTYPE_STR_FTYPE_STR_AND_GUID: {
    ParseState.PARTITION_NAME
  },
  ParseState.PREPARER: {
    ParseState.APPLICATION,
    ParseState.DATA_SIZE
  },
  ParseState.PUBLISHER: {
    ParseState.APPLICATION,
    ParseState.DATA_SIZE,
    ParseState.PREPARER
  },
  ParseState.SECTOR_SIZE: {
    ParseState.VOLUME_NAME
  },
  ParseState.SIGNATURE_MISSING: {
    ParseState._PARTITION_END
  },
  ParseState.SOLARIS_SPARC_DISKLABEL: {
    ParseState._PARTITION_START
  },
  ParseState.TAR_ARCHIVE: {
    ParseState._COMPRESSION_END,
    ParseState._COMPRESSION_START,
    ParseState._DISK_END
  },
  ParseState.UDF_RECOGNITION_SEQUENCE_MISSINGLOC: {
    #This one probably indicates a file system descent; but, it's self-described as 'unable to locate anchor descriptor'.
    ParseState._FILE_SYSTEM_START
  },
  ParseState.UDF_VERSION: {
    ParseState._FILE_SYSTEM_END
  },
  ParseState.VALIDATION_ENTRY_MISSING: {
    ParseState._EL_TORITO_END
  },
  ParseState.VOLUME_NAME: {
    ParseState._FILE_SYSTEM_END,
    ParseState.APPLICATION,
    ParseState.DATA_SIZE,
    ParseState.PARTITION_META,
    ParseState.PREPARER,
    ParseState.PUBLISHER,
    ParseState.UDF_VERSION,
    ParseState.VOLUME_SIZE
  },
  ParseState.VOLUME_SIZE: {
    ParseState._FILE_SYSTEM_END,
    ParseState._FILE_SYSTEM_START,
    ParseState._PARTITION_SYSTEM_START,
    ParseState.PARTITION_META,
    ParseState.VOLUME_NAME
  }
}

#These regexen are for byte strings because some free-form text (like generating application) includes non-ASCII characters (e.g. a copyright symbol).
rx_additional_primary_volume_descriptor   = re.compile(br"^Additional Primary Volume Descriptor$")
rx_application                            = re.compile(br"^Application +\"(?P<application>.+)\"$")
rx_blank_medium                           = re.compile(br"^Blank disk/medium$")
rx_boot_loader                            = re.compile(br"^(?P<boot_loader_type>(FreeBSD|ISOLINUX|LILO|SYSLINUX|Windows / MS-DOS|Windows 95/98/ME|Windows NTLDR)) boot loader.*$")
rx_boot_record                            = re.compile(br"^(?P<boot_record_type>.+) boot record, catalog at (?P<offset_in_sectors>\d+)$")
rx_bootable_floppy_image                  = re.compile(br"^Bootable (?P<floppy_size>.+) floppy image, starts at (?P<boot_offset_in_sectors>\d+), preloads (?P<preload_byte_count>\d+) bytes$")
rx_bootable_hard_disk_image               = re.compile(br"^Bootable hard disk image, starts at (?P<boot_offset_in_sectors>\d+), preloads (?P<preload_byte_count>\d+) bytes$")
rx_bootable_nonemulated_image             = re.compile(br"^Bootable non-emulated image, starts at (?P<boot_offset_in_sectors>\d+), preloads (?P<preload_count_unitless>\d+) (?P<preload_count_unit>.+)$")
rx_bsd_disklabel                          = re.compile(br"^BSD disklabel \(at sector (?P<sector>)\d+\), \d+ partitions$")
rx_cpio_archive                           = re.compile(br"^cpio archive(.*)$")
rx_data_size                              = re.compile(br"^Data size.+\((?P<num_bytes>\d+) bytes, (?P<block_count>\d+) blocks of (?P<bytes_per_block_unitless>\d+) (?P<bytes_per_block_unit>.+)\)$")
rx_data_size_no_comma                     = re.compile(br"^Data size (?P<num_bytes>\d+) bytes \((?P<block_count>\d+) blocks of (?P<bytes_per_block_unitless>\d+) (?P<bytes_per_block_unit>.+)\)$")
rx_descriptor_type                        = re.compile(br"^Descriptor type (?P<descriptor_type>\d+) at sector (?P<descriptor_offset_sector>\d+)$")
rx_disk_meta                              = re.compile(br"^Regular file, size (?P<human_readable_size>\d.+B) \((?P<bytes_in_image>\d+) bytes\)$")
rx_disk_guid                              = re.compile(br"^Disk GUID (?P<guid>[-0-9A-F]+)$")
rx_disk_size                              = re.compile(br"^Disk size.+ \((?P<num_bytes>\d+) bytes, (?P<num_blocks>\d+) (?P<block_unit>blocks|sectors).*\)$")
rx_file_system_uuid                       = re.compile(br"^UUID (?P<uuid>[-0-9A-F]+|nil)(.*)$")
rx_file_system_includes                   = re.compile(br"^Includes the disklabel and boot code$")  #Phrase hard-coding matches disktype unix.c.
rx_fs_type_str                            = re.compile(br"^(?P<ftype_str>.+) file system(?P<misc>.*)$")
rx_fs_type_str_misc_offset                = re.compile(br"(?P<bytes_unitless>\d+) (?P<bytes_unit>.iB) offset")
rx_gzip                                   = re.compile(br"^gzip-compressed data at sector (?P<sector>\d+)$")
rx_input_file                             = re.compile(br"^--- (?P<filepath>.+)$")
rx_hfs_wrapper                            = re.compile(br"^HFS wrapper for (?P<ftype_label>.+)$")
rx_iso9660_extension                      = re.compile(br"^(?P<extension>.+) extension, volume name \"(?P<volume_name>.*)\"$")
rx_last_mounted                           = re.compile(br"^Last mounted at \"(?P<filepath>.+)\"$")
rx_no_type_and_creator_code               = re.compile(br"^No type and creator code$")
rx_partition_blank_check                  = re.compile(br"^First (?P<range>.+) are blank")
rx_partition_guid                         = re.compile(br"^Partition GUID (?P<guid>[-0-9A-F]+)$")
rx_partition_includes                     = re.compile(br"^Includes the disklabel$")  #Phrase hard-coding matches disktype unix.c.
rx_partition_map                          = re.compile(br"^(?P<pstype_str>.+) partition map.*$")
rx_partition_meta_no_size_summary         = re.compile(br"^Partition (?P<partition_index>.+):.+(?P<partition_size_unitless>\d+) (?P<partition_size_unit>.+) \((?P<num_blocks_distance>\d+) (?P<block_unit>(sectors|clusters)) from (?P<from>\d+)(?P<bootable>(, bootable)?)\)")
rx_partition_meta_size_summary            = re.compile(br"^Partition (?P<partition_index>.+):.+\((?P<partition_size_unitless>\d+) (?P<partition_size_unit>.+), (?P<num_blocks_distance>\d+) (?P<block_unit>(sectors|clusters)) from (?P<from>\d+)(?P<bootable>(, bootable)?)\)")
rx_partition_name                         = re.compile(br"^Partition Name \"(?P<partition_name>.+)\"$")
rx_partition_ptype_and_ptype_str          = re.compile(br"^Type (?P<ptype>(0x[0-9A-Fa-f]{2}|\d+)) \((?P<ptype_label>.+)\)$")
rx_partition_ptype_int                    = re.compile(br"^Type (?P<ptype_label>\d+)$")
rx_partition_ptype_str                    = re.compile(br"^Type \"(?P<ptype_label>.+)\"$")
rx_partition_ptype_str_and_guid           = re.compile(br"^Type (?P<ptype_label>.+) \(GUID (?P<guid>[-0-9A-F]+)\)$")
rx_partition_ptype_str_ftype_str_and_guid = re.compile(br"^Type (?P<ptype_label>.+) \((?P<ftype_str>.+)\) \(GUID (?P<guid>[-0-9A-F]+)\)$")
rx_partition_unused                       = re.compile(br"^Partition (?P<partition_index>.+): unused$")
rx_platform_system_type                   = re.compile(br"^Platform (?P<platform_encoded>.+) \((?P<platform_decoded>.+)\), System Type (?P<system_type_encoded>.+) \((?P<system_type_decoded>.+)\)$")
rx_preparer                               = re.compile(br"^Preparer +\"(?P<preparer>.+)\"$")
rx_publisher                              = re.compile(br"^Publisher +\"(?P<publisher>.+)\"$")
rx_sector_size                            = re.compile(br"^Sector size (?P<sector_size>\d+) bytes$")
rx_signature_missing                      = re.compile(br"^Signature missing$")
rx_solaris_sparc_disklabel                = re.compile(br"^Solaris SPARC disklabel$")
rx_tar_archive                            = re.compile(br"^(GNU|Pre-POSIX) tar archive$")
rx_udf_recognition_sequence_missingloc    = re.compile(br"^UDF recognition sequence, unable to locate anchor descriptor$")
rx_udf_version                            = re.compile(br"^UDF version (?P<version>.+)$")
rx_validation_entry_missing               = re.compile(br"^Validation entry missing$")
rx_volume_name                            = re.compile(br"^Volume name \"(?P<volume_name>.*)\"(?P<misc>.*)$")
rx_volume_size_blocks_or_sectors          = re.compile(br"^Volume size.+ \((?P<num_bytes>\d+) bytes, (?P<num_blocks>\d+) (?P<block_unit>blocks|sectors).*\)$")
rx_volume_size_clusters                   = re.compile(br"^Volume size.+ \((?P<num_bytes>\d+) bytes, (?P<num_clusters>\d+) clusters of (?P<bytes_per_cluster_unitless>\d+) (?P<bytes_per_cluster_unit>.+)\)$")
rx_volume_size_clusters_no_summary        = re.compile(br"^Volume size.+ \((?P<num_clusters>\d+) clusters of (?P<bytes_per_cluster_unitless>\d+) (?P<bytes_per_cluster_unit>.+)\)$")

class Parser(object):
    def __init__(self):
        """State variables are initialized at the top of the parse() method."""
        pass

    def debug_level_stack(self):
        for (stack_level, level) in enumerate(self._level_stack):
            _logger.debug("self._level_stack[%d] = %s." % (stack_level, level))

    def debug_object_stack(self):
        for (stack_level, obj) in enumerate(self._object_stack):
            _logger.debug("self._object_stack[%d] = %s." % (stack_level, obj))

    def derive_volume_byte_run(self, vobj, num_bytes):
        """This code is repeated between FS_TYPE_STR, DATA_SIZE, VOLUME_SIZE state actions."""
        vbr = vobj.byte_runs[0]
        vbr.len = num_bytes
        cbr = self.get_container_byte_run()
        #If volume partition_offset information is absent, say volume encompasses whole container.
        if vobj.partition_offset is None:
            if not cbr is None:
                if cbr.len == vbr.len:
                    vobj.partition_offset = cbr.img_offset #TODO DFXML documentation may need to clarify whether partition_offset is always absolute to the input disk image, or relative to the beginning of the nearest containing disk image (e.g. with an El Torito emulated image).  Here, I intend for it always to be an absolute address.
                    vbr.img_offset = cbr.img_offset
        else:
            vbr.img_offset = vobj.partition_offset

    def get_container_byte_run(self):
        """
        Returns the byte run closest to the top of the object stack that has both img_offset and len defined.
        """
        #cobj - containing object
        cbr = None #Containing object's byte run
        for cobj in reversed(self._object_stack[:-1]):
            cbr = cobj.byte_runs[0]
            if not None in (cbr.img_offset, cbr.len):
                break
        return cbr

    def get_image_size(self):
        """Returns size of entire input disk image (not any nested disk image) from object stack."""

        image_size = None
        if len(self._object_stack) < 2:
            _logger.debug("get_image_size: len(self._object_stack) == %d." % len(self._object_stack))
            return None
        if not isinstance(self._object_stack[1], DiskImageObject):
            _logger.debug("get_image_size: type(self._object_stack[1]) == %r." % type(self._object_stack[1]))
            raise ValueError("self._object_stack[1] is not a DiskImageObject.")
        diobj = self._object_stack[1]
        if len(diobj.byte_runs) > 0:
            image_size = diobj.byte_runs[0].len
        if image_size is None:
            _logger.debug("get_image_size: diobj.byte_runs[0] == %r." % diobj.byte_runs[0])
        return image_size

    def parse(self, fh):
        self._state = ParseState._INPUT_START
        self._line_no = None  #1-based counter.  (Defining: line 0 is before beginning of file.)
        self._last_indentation = None
        self._current_indentation = None

        #The object stack is an object stack of DFXML Objects with .append() methods, and potential DFXML Objects defined in this script.
        self._object_stack = []

        #The level stack is a (nearly-)parallel list to the object stack.  It's necessary for now because DFXML doesn't have elements for partition systems, partitions, or other "parsing levels" (indentation levels) illustrated in disktype output.
        #The level stack is also necessary because indentation level needs to be tracked for the various encountered states.
        #Members and types: ParseState; indentation count (int or NoneType); line number (int)
        self._level_stack = [(ParseState._INPUT_START, None, 0)]

        dobj = Objects.DFXMLObject(version="1.1.1")
        dobj.program = os.path.basename(sys.argv[0])
        dobj.program_version = __version__
        dobj.command_line = " ".join(sys.argv)
        dobj.add_namespace("dfxmlext", XMLNS_DFXML_EXT)
        self._object_stack.append(dobj)

        #Some of the parsing expressions can match at multiple points, due to free-form text (usually in name fields).  Handle those cases with "_handle_foo" subroutines here.
        def _handle_application(maybe_match):
            self.transition(ParseState.APPLICATION)
            #Nop.  Information not recorded in DFXML.

        def _handle_partition_ptype_and_ptype_str(maybe_match):
            self.transition(ParseState.PARTITION_PTYPE_AND_PTYPE_STR)
            ptype = maybe_match.group("ptype").decode("utf-8")
            if ptype.startswith("0x"):
                self._object_stack[-1].ptype = int(ptype, base=16)
            else:
                self._object_stack[-1].ptype = int(ptype)
            self._object_stack[-1].ptype_str = maybe_match.group("ptype_label").decode("utf-8")

        def _handle_publisher(maybe_match):
            self.transition(ParseState.PUBLISHER)
            #Nop.  Information not recorded in DFXML.

        def _handle_volume_name(maybe_match):
            self.transition(ParseState.VOLUME_NAME)
            #Nop.  Information not recorded in DFXML.

        #Consume the input file handle lines.
        for (line_no, line) in enumerate(fh):
            _logger.debug("Parsing: %r." % line)
            self._line_no = line_no+1

            self.debug_level_stack()
            self.debug_object_stack()

            cleaned_line = line.strip()

            if cleaned_line == b"":
                #Blank input line is last input line; pop whole stack.
                _logger.debug("BLANK LINE - popping stack")
                _logger.debug("self._level_stack = %r." % self._level_stack)
                while self._level_stack[-1][0] != ParseState._INPUT_START:
                    self.pop_level()
                continue

            #Indentation matters.  Also, in some cases, long trails of whitespace are produced (e.g. 2009-m57-patents-redacted-terry-2009-12-11-002), so we need at least rstrip().  Full strip() is needed for cleaned_line to prevent some abiguities (e.g. rx_partition_ptype*, which starts "Type" matching rx_platform_system_type, which later contains "Type").
            self._last_indentation = self._current_indentation
            self._current_indentation = len(line) - len(line.lstrip())

            if not self._last_indentation is None and self._current_indentation < self._last_indentation:
                _logger.debug("DEINDENT")
                _logger.debug("  %r -> %r" % (self._last_indentation, self._current_indentation))
                #GPT metadata lines are indented before partitions are enumerated.  Don't close the partition system (i.e. pop levels) in that case.
                in_gpt_psobj = None
                for obj in reversed(self._object_stack):
                    if isinstance(obj, PartitionSystemObject):
                        in_gpt_psobj = (obj.pstype_str == "gpt")
                        break
                if in_gpt_psobj and self._level_stack[-1][0] == ParseState._PARTITION_SYSTEM_START:
                    _logger.debug("In GPT partition table.  Not popping level.")
                else:
                    #There used to be an assumption that a single partition wouldn't contain multiple file systems.  However, there are "Wrapper" file systems used in some cases (observed once on an Apple-partitioned CD that wrapped an HFS Plus file system within an HFS file system; see NSRL sample 10002-1.txt).  Check for that case, then fall through if not in that case.
                    maybe_match0 = rx_hfs_wrapper.search(cleaned_line)
                    if maybe_match0 is None:
                        #We're not in a wrapper.  Continue popping, to the topmost level with a matching indentation.
                        while self._current_indentation < self._level_stack[-1][1]:
                            self.pop_level()
                        #After that while loop completes, we've closed inner levels up to the container we actually wanted to close.
                    self.pop_level()
                _logger.debug("Done handling deindent effects.")

            maybe_match = rx_additional_primary_volume_descriptor.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.ADDITIONAL_PRIMARY_VOLUME_DESCRIPTOR)
                #Nop.  No further information provided in this pattern.
                continue

            maybe_match = rx_application.search(cleaned_line)
            if not maybe_match is None:
                _handle_application(maybe_match)
                continue

            maybe_match = rx_blank_medium.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.BLANK_MEDIUM)
                #Nop.
                continue

            maybe_match = rx_boot_loader.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.BOOT_LOADER)
                #Nop.
                continue

            maybe_match = rx_boot_record.search(cleaned_line)
            if not maybe_match is None:
                if maybe_match.group("boot_record_type").decode("utf-8") == "El Torito":
                    self.transition(ParseState._EL_TORITO_START)
                self.transition(ParseState.BOOT_RECORD)
                continue

            #This expression only matches on an El Torito boot catalog (see Disktype source, cdrom.c).
            maybe_match = rx_bootable_floppy_image.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState._DISK_START)
                self.transition(ParseState.BOOTABLE_FLOPPY_IMAGE)
                diobj = self._object_stack[-1]
                assert isinstance(diobj, DiskImageObject)

                vobj = self._object_stack[-2]
                if not isinstance(vobj, Objects.VolumeObject):
                    raise ValueError("Object stack confusion: Expecting object stack's last two members to be Objects.VolumeObject, DiskImageObject.  Instead they are: %r." % (type(self._object_stack[-2]), type(self._object_stack[-1])))

                diobj.sector_size = 512

                dibr = diobj.byte_runs[0]

                #"Sectors" are ISO9660-level sectors; recorded as blocks in the volume object.
                dibr.img_offset = int(maybe_match.group("boot_offset_in_sectors")) * vobj.block_size

                floppy_size = maybe_match.group("floppy_size").decode("utf-8")
                dibr.len = {
                  "1.2M":  1228800,
                  "1.44M": 1474560,
                  "2.88M": 2949120
                }[floppy_size]
                continue

            #This expression behaves much like the nonemulated expression in the next match block.  However, one sample of this image contained an indicator of a FAT16 file system (NSRL sample 11130-1).  Disktype didn't seem to think there was a FAT file system there, though.
            maybe_match = rx_bootable_hard_disk_image.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState._DISK_START)
                self.transition(ParseState.BOOTABLE_HARD_DISK_IMAGE)

                diobj = self._object_stack[-1]
                assert isinstance(diobj, DiskImageObject)
                vobj = self._object_stack[-2]
                assert isinstance(vobj, Objects.VolumeObject)

                dibr = diobj.byte_runs[0]
                #"Sectors" are ISO9660-level sectors; recorded as blocks in the volume object.
                dibr.img_offset = int(maybe_match.group("boot_offset_in_sectors")) * vobj.block_size
                continue

            #This expression only matches on an El Torito boot catalog (see Disktype source, cdrom.c).
            maybe_match = rx_bootable_nonemulated_image.search(cleaned_line)
            if not maybe_match is None:
                #The other "Bootable" regex (rx_bootable_floppy_image) indicates an emulated disk image, so that match triggers a transition to _DISK_START.  This regex, for non-emulated images, doesn't seem to contain further partition/file systems, but for symmetry's sake it will also transition to _DISK_START.
                self.transition(ParseState._DISK_START)
                self.transition(ParseState.BOOTABLE_NONEMULATED_IMAGE)

                diobj = self._object_stack[-1]
                assert isinstance(diobj, DiskImageObject)
                vobj = self._object_stack[-2]
                assert isinstance(vobj, Objects.VolumeObject)

                dibr = diobj.byte_runs[0]
                #"Sectors" are ISO9660-level sectors; recorded as blocks in the volume object.
                dibr.img_offset = int(maybe_match.group("boot_offset_in_sectors")) * vobj.block_size
                continue

            maybe_match = rx_bsd_disklabel.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState._PARTITION_SYSTEM_START)
                self.transition(ParseState.BSD_DISKLABEL)

                psobj = self._object_stack[-1]
                assert isinstance(psobj, PartitionSystemObject)

                psobj.pstype_str = "bsd"

                pstel = ET.Element("dfxmlext:pstype_str")
                pstel.text = psobj.pstype_str
                self._object_stack[0].externals.append(pstel) #TODO Maybe enqueue all the encountered partition systems into a set?

                #TODO Set up byte run for partition system?
                continue

            maybe_match = rx_cpio_archive.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.CPIO_ARCHIVE)
                #Nop.
                continue

            maybe_match = rx_data_size.search(cleaned_line) or rx_data_size_no_comma.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.DATA_SIZE)
                assert isinstance(self._object_stack[-1], Objects.VolumeObject)

                unit = maybe_match.group("bytes_per_block_unit").decode("utf-8")
                bytes_per_block_unit = block_units[unit]

                self._object_stack[-1].block_size = int(maybe_match.group("bytes_per_block_unitless")) * bytes_per_block_unit
                self._object_stack[-1].block_count = int(maybe_match.group("block_count"))

                num_bytes = int(maybe_match.group("num_bytes"))
                self.derive_volume_byte_run(self._object_stack[-1], num_bytes)
                continue

            maybe_match = rx_descriptor_type.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.DESCRIPTOR_TYPE)
                #TODO Decode type?
                continue

            maybe_match = rx_disk_guid.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.DISK_GUID)
                guid = maybe_match.group("guid").decode("utf-8")
                if isinstance(self._object_stack[-1], PartitionSystemObject):
                    self._object_stack[-1].guid = guid
                else:
                    _logger.info("Current parsing level: %r." % self._level_stack[-1][0])
                    raise NotImplementedError("Disk GUID provided at unexpected parsing level.  Expected partition system.")
                continue

            maybe_match = rx_disk_meta.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.DISK_META)
                if not len(self._object_stack) == 2:
                    raise ValueError("Expecting object stack to have just two items.  It currently has %d: %r." % (len(self._object_stack), self._object_stack))
                dibr = self._object_stack[-1].byte_runs[0]
                dibr.img_offset = 0
                dibr.len = int(maybe_match.group("bytes_in_image"))

                dibrel = dibr.to_Element()
                dibrel.tag = "dfxmlext:disk_image_byte_runs"
                self._object_stack[0].externals.append(dibrel)
                continue

            maybe_match = rx_disk_size.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.DISK_SIZE)
                psobj = self._object_stack[-1]
                if not isinstance(psobj, PartitionSystemObject):
                    _logger.info("Current parsing level: %r." % self._level_stack[-1][0])
                    raise NotImplementedError("'Disk size' line provided at unexpected parsing level.  Expected partition system.")
                psbr = psobj.byte_runs[0]
                psbr.len = int(maybe_match.group("num_bytes"))
                continue

            maybe_match = rx_file_system_uuid.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.FILE_SYSTEM_UUID)
                uuid = maybe_match.group("uuid").decode("utf-8")
                vobj = self._object_stack[-1]
                if not isinstance(vobj, Objects.VolumeObject):
                    _logger.info("Current parsing level: %r." % self._level_stack[-1][0])
                    raise NotImplementedError("UUID line provided at unexpected parsing level.  Expected file system.")
                uuidel = ET.Element("dfxmlext:uuid")
                if uuid == "nil":
                    uuidel.text = ""
                else:
                    uuidel.text = uuid
                vobj.externals.append(uuidel)
                continue

            maybe_match = rx_file_system_includes.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.FILE_SYSTEM_INCLUDES)
                #Nop.
                continue

            #rx_fs_type_str overlaps with other expressions that sometimes contain the free text "file system" without meaning to refer to a file system type.  Disambiguate.
            maybe_match = rx_fs_type_str.search(cleaned_line)
            if not maybe_match is None:
                maybe_match2 = rx_partition_ptype_and_ptype_str.search(cleaned_line)
                #The logic for ParseState.PARTITION_PTYPE_AND_PTYPE_STR (etc.) needs to be broken out into an internal function just because it can be reached at two points in this loop.
                if not maybe_match2 is None:
                    _handle_partition_ptype_and_ptype_str(maybe_match2)
                    continue
                if cleaned_line.startswith(b"Type"):
                    raise NotImplementedError("This appears to be a partition type, but the logic to handle it is not implemented yet, for lack of test cases.")

                maybe_match2 = rx_application.search(cleaned_line)
                if not maybe_match2 is None:
                    _handle_application(maybe_match2)
                    continue

                maybe_match2 = rx_publisher.search(cleaned_line)
                if not maybe_match2 is None:
                    _handle_publisher(maybe_match2)
                    continue

                maybe_match2 = rx_volume_name.search(cleaned_line)
                if not maybe_match2 is None:
                    _handle_volume_name(maybe_match2)
                    continue

                if self._current_indentation == 0:
                    #This is a file system outside of other partition managers (a common case is ISO 9660).  Pop back up to disk level.
                    while self._level_stack[-1][0] != ParseState._DISK_START:
                        self.pop_level()
                self.transition(ParseState._FILE_SYSTEM_START)
                self.transition(ParseState.FS_TYPE_STR)

                vobj = self._object_stack[-1]
                ftype_str = maybe_match.group("ftype_str").decode("utf-8")
                vobj.ftype_str = ftype_str

                cbr = self.get_container_byte_run()

                #The ftype_str line sometimes contains extra geometric information after the file system name.  If present, use that to record the file system dimensions.
                file_system_in_partition = isinstance(self._object_stack[-2], PartitionObject)
                maybe_match_2 = rx_fs_type_str_misc_offset.search(line)
                if maybe_match_2 is None:
                    #There is no geometry information.  Rely on inheriting the file system dimensions from either the containing partiion; or, just consider the file system to span the whole disk.
                    if file_system_in_partition:
                        _logger.debug("Trusting the file system geometry is inherited from the containing partition.")
                    else:
                        _logger.debug("Treating the file system as spanning the containing object.")
                        vobj.partition_offset = cbr.img_offset
                elif ftype_str == "UFS":
                    #The 'offset' datum in UFS indicates the offset of the superblock from the start of the file system.  Before that offset can come bootloader code.
                    #Since UFS can be a file system for an unpartitioned disk, treat the within-image offset as 0 if not already defined.
                    _logger.debug("Skipping offset information due to different meaning for UFS.")
                    if not file_system_in_partition:
                        _logger.debug("Treating the UFS file system as spanning the containing object.")
                        vobj.partition_offset = cbr.img_offset
                else:
                    _logger.debug("File system type line includes offset.")
                    bytes_unit = maybe_match_2.group("bytes_unit").decode("utf-8")
                    bytes_per_unit = block_units[bytes_unit]
                    vobj.partition_offset = int(maybe_match_2.group("bytes_unitless")) * bytes_per_unit

                num_bytes = None #To be an integer
                if not None in (self._object_stack[-1].block_count, self._object_stack[-1].block_size):
                    #Say the volume size is the number of blocks times block size.
                    num_bytes = self._object_stack[-1].block_count * self._object_stack[-1].block_size
                else:
                    #Say the volume size is the remainder of the disk image after the partition offset.
                    num_bytes = self.get_image_size() - self._object_stack[-1].partition_offset
                self.derive_volume_byte_run(self._object_stack[-1], num_bytes)
                continue

            maybe_match = rx_gzip.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState._COMPRESSION_START)
                self.transition(ParseState.GZIP)
                #Nop otherwise.
                continue

            maybe_match = rx_input_file.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState._DISK_START)
                self.transition(ParseState.INPUT_FILE)
                filepath = maybe_match.group("filepath").decode("utf-8")
                self._object_stack[0].sources.append(filepath)
                continue

            maybe_match = rx_hfs_wrapper.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.HFS_WRAPPER)
                #Nop.  File system starts on next line.
                continue

            maybe_match = rx_iso9660_extension.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.ISO9660_EXTENSION)
                extel = ET.Element("dfxmlext:iso9660extension")
                extel.text = maybe_match.group("extension").decode("utf-8")
                vobj.externals.append(extel)
                #TODO Volume name not recorded for now.  May need to address character encoding issues.
                continue

            maybe_match = rx_last_mounted.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.LAST_MOUNTED)
                #Nop.  Information not recorded in DFXML.
                continue

            maybe_match = rx_no_type_and_creator_code.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.NO_TYPE_AND_CREATOR_CODE)
                #Nop.
                continue


            maybe_match = rx_partition_blank_check.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.PARTITION_BLANK_CHECK)
                #Nop.
                continue

            maybe_match = rx_partition_guid.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.PARTITION_GUID)
                pobj = self._object_stack[-1]
                assert isinstance(pobj, PartitionObject)
                pobj.guid = maybe_match.group("guid").decode("utf-8")
                continue

            maybe_match = rx_partition_includes.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.PARTITION_INCLUDES)
                #Nop.
                continue

            maybe_match = rx_partition_map.search(cleaned_line)
            if not maybe_match is None:
                if self._level_stack[-1][0] == ParseState._PARTITION_SYSTEM_START:
                    #GPT/DOS disk images can't use indentation to detect when the counterpart partition system has closed.  Handle closing here.
                    self.pop_level()
                self.transition(ParseState._PARTITION_SYSTEM_START)
                self.transition(ParseState.PARTITION_MAP)

                psobj = self._object_stack[-1]
                assert isinstance(psobj, PartitionSystemObject)

                psobj.pstype_str = {
                  b"Apple": "mac",
                  b"DOS/MBR": "dos",
                  b"GPT": "gpt"
                }[maybe_match.group("pstype_str")]

                #For easier (maybe?) records checks, pstype_str is appended to the top DFXMLObject without any volume associations; and then associated as appropriate to each child partition and file system.
                #TODO Solaris disk labels can be nested in partitions.  (See NSRL sample 16618-1.txt)  pstype_str elements currently get counted once per file system.  Should fix this.
                pstel = ET.Element("dfxmlext:pstype_str")
                pstel.text = psobj.pstype_str
                self._object_stack[0].externals.append(pstel) #TODO Maybe enqueue all the encountered partition systems into a set?
                continue

            maybe_match = rx_partition_meta_no_size_summary.search(cleaned_line) or rx_partition_meta_size_summary.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState._PARTITION_START)
                self.transition(ParseState.PARTITION_META)
                pobj = self._object_stack[-1]
                assert isinstance(pobj, PartitionObject)
                psobj = self._object_stack[-2]
                assert isinstance(psobj, PartitionSystemObject)

                pbr = pobj.byte_runs[0]

                pobj.block_count = int(maybe_match.group("num_blocks_distance"))
                #pobj.block_size is by default inherited from the partition system, in transition().  We'll recompute it here, though, if we have the information.

                pbr.len = int(maybe_match.group("partition_size_unitless")) * block_units[maybe_match.group("partition_size_unit").decode("utf-8")]

                if pobj.block_count > 0:
                    if pbr.len % pobj.block_count != 0:
                        _logger.info("Bytes in partition = %r." % pbr.len)
                        _logger.info("Block count = %r." % pobj.block_count)
                        _logger.error("Guessed block size = %r." % (1.0 * pbr.len) / pobj.block_count)
                        raise ValueError("Error in confirming block size from given information.")
                    pobj.block_size = pbr.len // pobj.block_count

                #It is possible at this point that the block size has not yet been determined for any of the containing levels.  (See e.g. Apple partition map NSRL sample '10002-1.txt' - first opportunity to infer block size is the first Partition definition.)  Back-fill block size if it's absent.
                if psobj.block_size is None:
                    psobj.block_size = pobj.block_size
                if self._object_stack[1].sector_size is None:
                    self._object_stack[1].sector_size = psobj.block_size

                pobj.partition_system_offset = int(maybe_match.group("from")) * pobj.block_size

                #Finally, determine img_offset of the partition (which needs to be computed relative to the img_offset of the partition system).
                psbr = psobj.byte_runs[0]
                pbr.img_offset = psbr.img_offset + pobj.partition_system_offset

                continue

            maybe_match = rx_partition_name.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.PARTITION_NAME)
                #TODO Partition name not recorded for now.  May need to address character encoding issues.
                continue

            maybe_match = rx_partition_ptype_int.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.PARTITION_PTYPE_INT)
                self._object_stack[-1].ptype = int(maybe_match.group("ptype_label"))
                continue

            maybe_match = rx_partition_ptype_str.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.PARTITION_PTYPE_STR)
                self._object_stack[-1].ptype_str = maybe_match.group("ptype_label").decode("utf-8")
                continue

            maybe_match = rx_partition_ptype_str_ftype_str_and_guid.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.PARTITION_PTYPE_STR_FTYPE_STR_AND_GUID)
                self._object_stack[-1].ptype_str = maybe_match.group("ptype_label").decode("utf-8")
                self._object_stack[-1].ftype_str = maybe_match.group("ftype_str").decode("utf-8")
                self._object_stack[-1].guid = maybe_match.group("guid").decode("utf-8")
                continue

            maybe_match = rx_partition_ptype_str_and_guid.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.PARTITION_PTYPE_STR_AND_GUID)
                self._object_stack[-1].ptype_str = maybe_match.group("ptype_label").decode("utf-8")
                self._object_stack[-1].guid = maybe_match.group("guid").decode("utf-8")
                continue

            maybe_match = rx_partition_ptype_and_ptype_str.search(cleaned_line)
            if not maybe_match is None:
                _handle_partition_ptype_and_ptype_str(maybe_match)
                continue

            maybe_match = rx_partition_unused.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState._PARTITION_START)
                self.transition(ParseState.PARTITION_UNUSED)
                #Nop.
                continue

            maybe_match = rx_platform_system_type.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.PLATFORM_SYSTEM_TYPE)
                #TODO Decode?
                continue

            maybe_match = rx_preparer.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.PREPARER)
                #Not currently recorded in DFXML.
                #Nop.
                continue

            maybe_match = rx_publisher.search(cleaned_line)
            if not maybe_match is None:
                _handle_publisher(maybe_match)
                continue

            maybe_match = rx_sector_size.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.SECTOR_SIZE)
                if self._level_stack[-1][0] == ParseState._FILE_SYSTEM_START:
                    self._object_stack[-1].sector_size = int(maybe_match.group("sector_size"))
                else:
                    raise NotImplementedError("Currently unspecified: How to integrate sector size information in level %r." % self._level_stack[-1][0])
                continue

            maybe_match = rx_signature_missing.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.SIGNATURE_MISSING)
                #Nop.
                continue

            maybe_match = rx_solaris_sparc_disklabel.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState._PARTITION_SYSTEM_START)
                self.transition(ParseState.SOLARIS_SPARC_DISKLABEL)

                psobj = self._object_stack[-1]
                assert isinstance(psobj, PartitionSystemObject)

                psobj.pstype_str = "sun"
                pstel = ET.Element("dfxmlext:pstype_str")
                pstel.text = psobj.pstype_str
                self._object_stack[0].externals.append(pstel)
                continue

            maybe_match = rx_tar_archive.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.TAR_ARCHIVE)
                #Nop.
                continue

            maybe_match = rx_udf_recognition_sequence_missingloc.search(cleaned_line)
            if not maybe_match is None:
                if self._current_indentation == 0:
                    #This is a file system outside of other partition managers (UDF and ISO 9660 are common cases of this).  Pop back up to disk level.
                    while self._level_stack[-1][0] != ParseState._DISK_START:
                        self.pop_level()
                self.transition(ParseState.UDF_RECOGNITION_SEQUENCE_MISSINGLOC)
                #Nop.
                continue

            maybe_match = rx_udf_version.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.UDF_VERSION)
                #Nop.
                continue

            maybe_match = rx_validation_entry_missing.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.VALIDATION_ENTRY_MISSING)
                #Nop.
                continue

            maybe_match = rx_volume_name.search(cleaned_line)
            if not maybe_match is None:
                _handle_volume_name(maybe_match)
                continue

            maybe_match = rx_volume_size_blocks_or_sectors.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.VOLUME_SIZE)
                vobj = self._object_stack[-1]
                assert isinstance(vobj, Objects.VolumeObject)

                vobj.block_count = int(maybe_match.group("num_blocks"))
                volume_num_bytes = int(maybe_match.group("num_bytes"))
                vobj.block_size = volume_num_bytes // self._object_stack[-1].block_count

                #Treat the VolumeObject byte run as the *file system* dimensions.  The *partition's* (or other container's, e.g. the disk's) dimensions can be bigger than the file systems, but those dimensions are recorded separately in extension elements.
                self.derive_volume_byte_run(self._object_stack[-1], volume_num_bytes)

                continue

            maybe_match = rx_volume_size_clusters.search(cleaned_line) or rx_volume_size_clusters_no_summary.search(cleaned_line)
            if not maybe_match is None:
                self.transition(ParseState.VOLUME_SIZE)
                vobj = self._object_stack[-1]
                assert isinstance(vobj, Objects.VolumeObject)

                vobj.block_count = int(maybe_match.group("num_clusters"))
                vobj.block_size = int(maybe_match.group("bytes_per_cluster_unitless")) * block_units[maybe_match.group("bytes_per_cluster_unit").decode("utf-8")]

                if "num_bytes" in maybe_match.groupdict():
                    #Double-check reported Disktype data, if available (only appears in one of the rx_volume_size_ regexen).
                    num_bytes = int(maybe_match.group("num_bytes"))
                    if num_bytes != vobj.block_count * vobj.block_size:
                        #Maybe this should be a warning?
                        raise ValueError("The number of bytes disktype does not match the cluster size and count: %r vs. %r * %r." % (num_bytes, vobj.block_count, vobj.block_size))

                self.derive_volume_byte_run(vobj, num_bytes)
                continue

            raise ValueError("Unparsed line: %r." % line)
        self.transition(ParseState._INPUT_END)

        return dobj

    def pop_level(self):
        """Pops up one level in the storage system stack (e.g. file system to partition).  Uses self._level_stack to determine whether object stack is also popped.  Transitions parsing state to appropriate _..._END member of ParseState."""

        level_popped = None
        object_popped = None
        if self._level_stack[-1][0] == ParseState._COMPRESSION_START:
            self.transition(ParseState._COMPRESSION_END)
            level_popped = self._level_stack.pop()
            #object_popped = self._object_stack.pop()  #No object in compression.  Yet.
        elif self._level_stack[-1][0] == ParseState._FILE_SYSTEM_START:
            self.transition(ParseState._FILE_SYSTEM_END)
            level_popped = self._level_stack.pop()
            object_popped = self._object_stack.pop()
        elif self._level_stack[-1][0] == ParseState._PARTITION_START:
            self.transition(ParseState._PARTITION_END)
            level_popped = self._level_stack.pop()
            object_popped = self._object_stack.pop()
        elif self._level_stack[-1][0] == ParseState._PARTITION_SYSTEM_START:
            self.transition(ParseState._PARTITION_SYSTEM_END)
            level_popped = self._level_stack.pop()
            object_popped = self._object_stack.pop()
        elif self._level_stack[-1][0] == ParseState._EL_TORITO_START:
            self.transition(ParseState._EL_TORITO_END)
            level_popped = self._level_stack.pop()
            #object_popped = self._object_stack.pop()  #No object for El Torito boot records.  Yet.
        elif self._level_stack[-1][0] == ParseState._DISK_START:
            self.transition(ParseState._DISK_END)
            level_popped = self._level_stack.pop()
            object_popped = self._object_stack.pop()

        if level_popped is None:
            _logger.debug("No level popped.")
        else:
            _logger.debug("Level popped: %r." % (level_popped,))

        if object_popped is None:
            _logger.debug("No object popped.")
        else:
            _logger.debug("Object popped: %s." % (object_popped,))

        return (level_popped, object_popped)

    def transition(self, to_state):
        """
        Instantiate new members of object stack.

        To simplify byte run management: All byte_runs.append calls are made in this function.
        """

        _logger.debug("Transitioning to %r." % to_state)

        if not to_state in state_transitions[self._state]:
            raise ValueError("Input line %r: Unimplemented transition: %r -> %r." % (self._line_no, self._state, to_state))
        self._state = to_state

        level_pushed = None
        if to_state in {
          ParseState._DISK_START,
          ParseState._PARTITION_SYSTEM_START,
          ParseState._PARTITION_START,
          ParseState._FILE_SYSTEM_START,
          ParseState._EL_TORITO_START,
          ParseState._COMPRESSION_START
        }:
            level_pushed = (to_state, self._current_indentation, self._line_no)
            self._level_stack.append(level_pushed)

        object_pushed = None

        if to_state == ParseState._DISK_START:
            diobj = DiskImageObject()
            object_pushed = diobj
            self._object_stack.append(diobj)

            dibr = Objects.ByteRun()
            diobj.byte_runs.append(dibr)

        if to_state == ParseState._PARTITION_SYSTEM_START:
            psobj = PartitionSystemObject()
            object_pushed = psobj
            self._object_stack.append(psobj)

            psbr = Objects.ByteRun()
            psobj.byte_runs.append(psbr)

            if isinstance(self._object_stack[-2], PartitionObject):
                #Solaris SPARC disklabels can appear in a partition, nesting a partition system.  If this has happened, inherit the container's byte run.
                pobj = self._object_stack[-2]
                pbr = pobj.byte_runs[0]
                psbr.img_offset = pbr.img_offset
                psbr.len = pbr.len
            elif isinstance(self._object_stack[-2], DiskImageObject):
                #El Torito bootable images are disk images in the middle of the input image.  Thus, we must work relative to any containing disk image.
                diobj = self._object_stack[-2]
                dibr = diobj.byte_runs[0]
                psbr.img_offset = dibr.img_offset

                #El Torito bootable images contain partition systems that reset the sector size.
                psobj.block_size = diobj.sector_size
            else:
                psbr.img_offset = 0

        if to_state == ParseState._PARTITION_START:
            pobj = PartitionObject()
            object_pushed = pobj
            self._object_stack.append(pobj)

            pbr = Objects.ByteRun()
            pobj.byte_runs.append(pbr)

            #PartitionObjects should only be within PartitionSystemObjects.
            psobj = self._object_stack[-2]
            assert isinstance(psobj, PartitionSystemObject)

            #This is mainly to catch El Torito re-assignments.
            if not psobj.block_size is None:
                pobj.block_size = psobj.block_size

        if to_state == ParseState._FILE_SYSTEM_START:
            vobj = Objects.VolumeObject()
            object_pushed = vobj
            self._object_stack[0].append(vobj)
            self._object_stack.append(vobj)

            vobj.byte_runs = Objects.ByteRuns()
            vbr = None
            #Byte-run append is handled at the end of this block, because of potential inheritance.

            if isinstance(self._object_stack[-3], PartitionSystemObject):
                psobj = self._object_stack[-3]
            else:
                psobj = None

            if isinstance(self._object_stack[-2], PartitionObject):
                pobj = self._object_stack[-2]
            else:
                pobj = None

            if not psobj is None:
                #Inherit.
                if not psobj.pstype_str is None:
                    pstel = ET.Element("dfxmlext:pstype_str")
                    pstel.text = psobj.pstype_str
                    vobj.externals.append(pstel)

            if not pobj is None:
                #Inherit.
                if not pobj.guid is None:
                    gel = ET.Element("dfxmlext:guid")
                    gel.text = pobj.guid
                    vobj.externals.append(gel)
                if not pobj.ptype is None:
                    ptel = ET.Element("dfxmlext:ptype")
                    ptel.text = str(pobj.ptype) #xml.etree requires strings for output.
                    vobj.externals.append(ptel)
                if not pobj.ptype_str is None:
                    ptel = ET.Element("dfxmlext:ptype_str")
                    ptel.text = pobj.ptype_str
                    vobj.externals.append(ptel)
                if not pobj.block_count is None:
                    vobj.block_count = pobj.block_count #NOTE: This may be overwritten.  A file system doesn't need to fill the partition.
                if not pobj.block_size is None:
                    vobj.block_size = pobj.block_size #NOTE: This may be overwritten.  A file system can have its own block(/cluster) size.
                if not pobj.ftype_str is None:
                    vobj.ftype_str = pobj.ftype_str
                pbr = pobj.byte_runs[0]
                if not None in (pbr.img_offset, pbr.len):
                    #The volume byte run may be updated by further information.  Keep the partition byte run handy, but in its own element.
                    vbr = copy.deepcopy(pbr)
                    vobj.partition_offset = pbr.img_offset
                    pbrel = pbr.to_Element()
                    pbrel.tag = "dfxmlext:partition_byte_run"
                    vobj.externals.append(pbrel)

            if vbr is None:
                #Treat volume as spanning whole containing disk image.
                cobj = None #Containing object
                object_stack_level = -1
                assert isinstance(self._object_stack[1], DiskImageObject) #Guarantee termination.
                while not isinstance(cobj, DiskImageObject):
                    object_stack_level -= 1
                    cobj = self._object_stack[object_stack_level]
                vbr = copy.deepcopy(cobj.byte_runs[0])
            vobj.byte_runs.append(vbr)

        if level_pushed is None:
            _logger.debug("No level pushed.")
        else:
            _logger.debug("Level pushed: %r." % (level_pushed,))
        if object_pushed is None:
            _logger.debug("No object pushed.")
        else:
            _logger.debug("Object pushed: %s." % object_pushed)

def main():
    with open(args.disktype_out_txt, "rb") as in_fh:
        parser = Parser()
        dobj = parser.parse(in_fh)
        dobj.print_dfxml()

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-d", "--debug", action="store_true")
    parser.add_argument("disktype_out_txt", help="Disktype stdout.")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO)

    main()
