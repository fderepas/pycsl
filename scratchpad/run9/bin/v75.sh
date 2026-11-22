#!/bin/bash
# v75: int76 (= main + u62 + u63) pre-gate (the two run #8 red planes, individually, full output) then battery C/D/E/F
export HEAVY_PRIO=1; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
H=/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh; T=/home/fabrice/git/pycsl-int76; O=/home/fabrice/git/pycsl/scratchpad/run9/v75; mkdir -p $O
cd $T
$H .venv/bin/python3 bin/check-directive-enforcement.py > $O/P-directive.log 2>&1; echo "$(date -u +%H:%MZ) P directive-enforcement rc=$?" >> $O/pre.txt
$H .venv/bin/python3 bin/check-stdlib-modules-verify.py > $O/P-stdlib.log 2>&1; echo "$(date -u +%H:%MZ) P stdlib-modules-verify rc=$?" >> $O/pre.txt
cd /home/fabrice/git/pycsl
BASE_BD=/home/fabrice/git/pycsl/scratchpad/run8/v73/bd-int BASE_MIR=/home/fabrice/git/pycsl/scratchpad/run8/v73/mir-int STEPS=CDEF bash scratchpad/run9/bin/battery.sh v75 $T /home/fabrice/git/pycsl
