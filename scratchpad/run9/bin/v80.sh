#!/bin/bash
# v80: int82 (= L21 + u70 + u72) battery A/C/D/E/F (PRIO, TMPDIR on the repo volume). Bases: v79 sweeps of int80 (emission == L21).
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/run9/tmp
export HEAVY_PRIO=1; cd /home/fabrice/git/pycsl
BASE_BD=/home/fabrice/git/pycsl/scratchpad/run9/v79/bd-int BASE_MIR=/home/fabrice/git/pycsl/scratchpad/run9/v79/mir-int bash scratchpad/run9/bin/battery.sh v80 /home/fabrice/git/pycsl-int82 /home/fabrice/git/pycsl
