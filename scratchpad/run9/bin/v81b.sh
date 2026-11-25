#!/bin/bash
# v81b: int83 (= L22 + u73 + u75) battery A/C/D/E/F (PRIO, TMPDIR on the repo volume). Bases: v80 sweeps of int82 (emission == L22).
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/run9/tmp
export HEAVY_PRIO=1; cd /home/fabrice/git/pycsl
BASE_BD=/home/fabrice/git/pycsl/scratchpad/run9/v80/bd-int BASE_MIR=/home/fabrice/git/pycsl/scratchpad/run9/v80/mir-int bash scratchpad/run9/bin/battery.sh v81b /home/fabrice/git/pycsl-int83f /home/fabrice/git/pycsl
