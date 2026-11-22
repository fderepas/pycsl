#!/bin/bash
# v76: int77 (= main L19 + u65) battery A/C/D/E/F (PRIO). Bases: v75 sweeps of int76 (= L19 emission; L19 src/bin/test-suite == int76's).
export HEAVY_PRIO=1; cd /home/fabrice/git/pycsl
BASE_BD=/home/fabrice/git/pycsl/scratchpad/run9/v75/bd-int BASE_MIR=/home/fabrice/git/pycsl/scratchpad/run9/v75/mir-int bash scratchpad/run9/bin/battery.sh v76 /home/fabrice/git/pycsl-int77 /home/fabrice/git/pycsl
