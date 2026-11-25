#!/bin/bash
# wit.sh <tag:tree> ... : full proof of witnesses 10530-10537 in each tree (cwd = tree root), logs in wit/<tag>/
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u77/scratchpad/u77/tmp
U=/home/fabrice/git/pycsl-u77/scratchpad/u77
OE=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
for a in "$@"; do tag=${a%%:*}; T=${a#*:}; mkdir -p $U/wit/$tag; cd $T || exit 2
  # the witnesses are taken from the u77 tree (a base tree does not have them)
  for f in /home/fabrice/git/pycsl-u77/test-suite/corpus/pycsl-reference/1053[0-7]_*.py; do
    n=$(basename $f .py); W=$U/wit/$tag/src; mkdir -p $W; cp $f $W/; cp /home/fabrice/git/pycsl-u77/test-suite/corpus/pycsl-reference/zu77a.py $W/
    fl=$(grep -m1 '^# pycsl-flags:' $f | sed 's/^# pycsl-flags://')
    o0=$(grep oom_kill $OE); timeout 3700 .venv/bin/python3 src/pycsl/pycsl.py $W/$n.py --import-path $W $fl > $U/wit/$tag/$n.log 2>&1; rc=$?
    o1=$(grep oom_kill $OE); echo "rc=$rc flags=[$fl] tree=$T oom0=[$o0] oom1=[$o1]" >> $U/wit/$tag/$n.log
    echo "$tag $n rc=$rc $(grep -m1 -oE 'All contracts formally proven|PYCSL-[A-Z0-9-]+|L3-tc ✗|Verification FAILED|FAIL[A-Z]*' $U/wit/$tag/$n.log)"
  done
done
echo WDONE
