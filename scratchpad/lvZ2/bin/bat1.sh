#!/bin/bash
# bat1.sh : ONE heavy job, sequential: S1 (T) spike sweep on snapshot lvZ2s, S2 R614 sweep on snapshot lvZ2rs
B=/home/fabrice/git/pycsl-lvZ2/scratchpad/lvZ2
ls /home/fabrice/git/pycsl-lvZ2s/src/pycsl/pycsl.py /home/fabrice/git/pycsl-lvZ2rs/src/pycsl/pycsl.py || exit 2
$B/bin/sweep.sh /home/fabrice/git/pycsl-lvZ2s $B/sw1
$B/bin/sweep.sh /home/fabrice/git/pycsl-lvZ2rs $B/swR
echo "BAT1-DONE $(date -u +%FT%TZ)" >> $B/sw1/status
