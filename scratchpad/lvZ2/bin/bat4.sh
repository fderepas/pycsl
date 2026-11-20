#!/bin/bash
# bat4.sh : ONE heavy NORMAL job: delta gates on the FINAL merged snapshot lvZ2f (sweep, witnesses x3, fidelity,
# fast planes incl. refusal-witness coverage with the final census rows, conformance)
B=/home/fabrice/git/pycsl-lvZ2/scratchpad/lvZ2
ls /home/fabrice/git/pycsl-lvZ2f/src/pycsl/pycsl.py || exit 2
$B/bin/bat2.sh /home/fabrice/git/pycsl-lvZ2f $B/f1 568
