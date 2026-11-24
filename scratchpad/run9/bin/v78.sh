#!/bin/bash
# v78: int79 (= L20 + V2D batch u64 + u66 + u69 + u71) battery A/C/D/E/F (PRIO). Bases: v77 sweeps of int78 (== L20 src / bin / test-suite).
export HEAVY_PRIO=1; cd /home/fabrice/git/pycsl
BASE_BD=/home/fabrice/git/pycsl/scratchpad/run9/v77/bd-int BASE_MIR=/home/fabrice/git/pycsl/scratchpad/run9/v77/mir-int bash scratchpad/run9/bin/battery.sh v78 /home/fabrice/git/pycsl-int79 /home/fabrice/git/pycsl
