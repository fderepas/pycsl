#!/bin/bash
# base.sh: base sweeps (root+pyref byte-diff, mirror) in the detached base tree pycsl-u74b (cwd = tree root)
S=/home/fabrice/git/pycsl-u74/scratchpad/u74/sw/base
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
cd /home/fabrice/git/pycsl-u74b || exit 2
echo "base start $(date -u) $(git log --oneline -1 | cut -c1-12)"
bin/byte-diff-sweep.sh $S/bd > $S/bd.log 2>&1; echo "base bd rc=$? $(tail -2 $S/bd.log | tr '\n' ' ')"
bin/mirror-emit-sweep.sh $S/mir > $S/mir.log 2>&1; echo "base mir rc=$? $(tail -1 $S/mir.log)"
echo "base done $(date -u)" > $S/done.txt
