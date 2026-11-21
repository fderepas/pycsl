#!/bin/bash
# bat3.sh : ONE heavy NORMAL job: full gates on the merged snapshot lvZ2g, then sweep + census + witnesses on the
# separable R614 snapshot lvZ2rs.
B=/home/fabrice/git/pycsl-lvZ2/scratchpad/lvZ2
ls /home/fabrice/git/pycsl-lvZ2g/src/pycsl/pycsl.py /home/fabrice/git/pycsl-lvZ2rs/src/pycsl/pycsl.py || exit 2
$B/bin/bat2.sh /home/fabrice/git/pycsl-lvZ2g $B/g1 12345678
$B/bin/bat2.sh /home/fabrice/git/pycsl-lvZ2rs $B/r1 123
echo "BAT3-DONE $(date -u +%FT%TZ)" >> $B/g1/summary.txt
