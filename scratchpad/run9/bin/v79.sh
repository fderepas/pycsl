#!/bin/bash
# v79: int80 (= L20 + V2D batch u64/u66/u69/u71 + u67 type_of_batch) battery A/C/D/E/F (PRIO), then the driver whole-file proof of the moved mirror file sertop.py on int80.
export HEAVY_PRIO=1; cd /home/fabrice/git/pycsl
BASE_BD=/home/fabrice/git/pycsl/scratchpad/run9/v77/bd-int BASE_MIR=/home/fabrice/git/pycsl/scratchpad/run9/v77/mir-int bash scratchpad/run9/bin/battery.sh v79 /home/fabrice/git/pycsl-int80 /home/fabrice/git/pycsl
PQ_ENV="HEAVY_PRIO=1 PYTHON_CPU_COUNT=4" bash scratchpad/run9/bin/proveq.sh /home/fabrice/git/pycsl-int80 v79p proof2why3/sertop.py
