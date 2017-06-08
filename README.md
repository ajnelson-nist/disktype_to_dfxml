# Disktype to DFXML

This project converts the output of the `disktype` tool into DFXML.

The primary script, `disktype_to_dfxml.py`, takes the pre-computed output of `disktype` and outputs XML.  A simple workflow to go from disk image to DFXML would be something like:

    disktype /path/to/image.img > disktype_output.txt
    python3 disktype_to_dfxml.py disktype_output.txt > disktype_output.dfxml

`xmllint` can be used to format the XML output for legibility.  A Bash one-liner that executes this whole workflow could be:

    python3 disktype_to_dfxml.py <(disktype /path/to/image.img) | xmllint --format - > disktype_output.dfxml

To run unit tests, run `make check`.


## Prerequisites

`disktype_to_dfxml.py` makes use of Python 3 features.  It has been tested on the `disktype` version as supplied in Ubuntu 16.04.
