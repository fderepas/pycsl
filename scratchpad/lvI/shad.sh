#!/bin/bash
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
L=/home/fabrice/git/pycsl-lvI/scratchpad/lvI
cd /home/fabrice/git/pycsl-lvI && python3 bin/check-shadowed-selfcalls.py --emit-dir $L/sw/mir_cand --verbose > $L/sw/shad_cand.txt 2>&1
cd /home/fabrice/git/pycsl-lvI-base && python3 bin/check-shadowed-selfcalls.py --emit-dir $L/sw/mir_base --verbose > $L/sw/shad_base.txt 2>&1
