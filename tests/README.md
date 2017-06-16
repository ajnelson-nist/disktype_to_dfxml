# Tests

The purpose of the tests in this directory is mainly to verify that `disktype_to_dfxml.py` runs on the supplied sample data.  In some cases, further details (e.g. file system starting offsets) are computed by hand from `disktype` output, with some out-of-band verification on the source data, and put into more thorough verification scripts.

The subdirectories here indicate the version of Disktype used to process the test subject disk images.  They produce slight variances given the same test subject disk.
* `macports` is for Disktype version 9 as packaged by MacPorts, port version "`9_2`".
* `ubuntu16.04` is for Disktype version 9 as packaged by Ubuntu 16.04, package version "`9-3`".

The disk images behind the sample `disktype` data generally comes from two sources currently.  Either the disk images are publicly available, with source locations recorded in the text files' Git history; or, the disk images are part of the [National Software Reference Library](https://www.nsrl.nist.gov/) collection (and those files are prefixed "`nsrl-`".  While the NSRL disk images are not available for download, access is available on request.
