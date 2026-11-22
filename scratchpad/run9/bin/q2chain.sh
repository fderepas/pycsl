#!/bin/bash
# wait for v75 battery to finish (slot 1 free), then the remaining 50 mirror files on int76, NORMAL (HEAVY_SHORT: FIFO with executors), PYTHON_CPU_COUNT=2
S=/home/fabrice/git/pycsl/scratchpad/run9/v75/summary.txt
until grep -q BATTERY-DONE $S 2>/dev/null; do sleep 60; done
cd /home/fabrice/git/pycsl && PQ_ENV="HEAVY_SHORT=1 PYTHON_CPU_COUNT=2" bash scratchpad/run9/bin/proveq.sh /home/fabrice/git/pycsl-int76 q2 $(cat scratchpad/run9/q2-files.txt)
