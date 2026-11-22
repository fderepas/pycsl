#!/bin/bash
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; cd /home/fabrice/git/pycsl-int76; V=/home/fabrice/git/pycsl/scratchpad/run9/vs
export PYTHON_CPU_COUNT=4
.venv/bin/python3 src/pycsl/pycsl.py $V/vt.py > $V/vt-full.log 2>&1; echo "full rc=$?"
for k in -1 0 1 2; do .venv/bin/python3 $V/../bin/vacshard.py /home/fabrice/git/pycsl-int76 $k 3 $V/vt.py > $V/vt-s$k.log 2>&1; echo "shard $k rc=$?"; done
