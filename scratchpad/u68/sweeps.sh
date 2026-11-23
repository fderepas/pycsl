#!/bin/bash
# base sweep (run9-u65 tree) then head sweep (u68 tree), each cwd = tree root, NORMAL heavy
H=/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh; O=/home/fabrice/git/pycsl-u68/scratchpad/u68/sw
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
(cd /home/fabrice/git/pycsl-u68b && PYTHON_CPU_COUNT=2 $H bin/byte-diff-sweep.sh $O/base > $O/base.log 2>&1); echo "base rc=$?" >> $O/done.txt
(cd /home/fabrice/git/pycsl-u68 && PYTHON_CPU_COUNT=2 $H bin/byte-diff-sweep.sh $O/head > $O/head.log 2>&1); echo "head rc=$?" >> $O/done.txt
echo END >> $O/done.txt
