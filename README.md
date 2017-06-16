# Disktype to DFXML

This project converts the output of the `disktype` tool into DFXML.

`disktype` reports on disk partitioning systems; partition dimensions, with partition table-level hints at contained file systems; file system presence, type, and dimensions; and nested boot images, with additional information noted at all of these levels.  This DFXML translator takes `disktype` output and reports file system information as a stream of `<volume>` elements, with some supplemental information on the containing partitions included.


## Usage

The primary script, `disktype_to_dfxml.py`, takes the pre-computed output of `disktype` and outputs XML.  A simple workflow to go from disk image to DFXML would be something like:

    disktype /path/to/image.img > disktype_output.txt
    python3 disktype_to_dfxml.py disktype_output.txt > disktype_output.dfxml

`xmllint` can be used to format the XML output for legibility.  A Bash one-liner that executes this whole workflow could be:

    python3 disktype_to_dfxml.py <(disktype /path/to/image.img) | xmllint --format - > disktype_output.dfxml


## Prerequisites

`disktype_to_dfxml.py` makes use of Python 3 features.  It has been tested on the `disktype` versions as supplied by Ubuntu 16.04, and as supplied by MacPorts.  The `deps/` directory includes package scripts that install prerequisite software.  If you have pre-computed `disktype` output, then you only need Python 3 to use this script.

Before usage, you will have to run these commands in the same directory as this README:

    git submodule init
    git submodule update


## Testing

To run unit tests, which are mostly demonstrations the script runs against sample `disktype` output, run `make check`.


## Reporting issues

`disktype_to_dfxml.py` was developed by translating `disktype` output generated from data at hand, instead of exhaustively reviewing the `disktype` code base for patterns.  Hence, there is potential for there to be coverage issues when running new `disktype` output through the script.

If you encounter an issue reading your own `disktype` output, it will be easiest to correct if you can provide the entirety of the `disktype` output that failed to translate.  *You may wish to review and/or scrub the Disktype content before emailing or publicly posting it.*

Bugs can be reported on the [Issues Tracker](https://github.com/ajnelson-nist/disktype_to_dfxml/issues), or by emailing this script's maintainer at: `alexander.nelson@nist.gov`.
