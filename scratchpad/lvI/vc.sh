#!/bin/bash
# vc.sh <mlw> <goal> <tag> : prove ONE goal (split) with Alt-Ergo then Z3 (NORMAL)
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
O=/home/fabrice/git/pycsl-lvI/scratchpad/lvI/fun/$3.log; : > $O
for P in "Alt-Ergo,2.6.3," "Z3,4.13.3,"; do
  echo "== $P" >> $O
  timeout 1200 why3 prove -a split_vc -P "$P" --timelimit 10 "$1" -T PyCSL_Program -G "$2" >> $O 2>&1; echo "rc=$?" >> $O
done
