#!/bin/bash
# v79F: re-run of v79's F (--slow planes) on int80 after the 21:35Z / 22:27Z /tmp quota incidents (TMPDIR on the repo volume), then the driver whole-file proof of sertop.py on int80
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/run9/tmp
export HEAVY_PRIO=1; cd /home/fabrice/git/pycsl
STEPS=F bash scratchpad/run9/bin/battery.sh v79 /home/fabrice/git/pycsl-int80 /home/fabrice/git/pycsl
PQ_ENV="HEAVY_PRIO=1 PYTHON_CPU_COUNT=4" bash scratchpad/run9/bin/proveq.sh /home/fabrice/git/pycsl-int80 v79p proof2why3/sertop.py
