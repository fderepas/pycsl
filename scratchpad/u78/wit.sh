#!/bin/bash
# wit.sh: full proofs (cwd = tree root pycsl-u78) of witnesses 10540-10545 and u77's PASS controls 10532 / 10535 / 10537; logs in wit/
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
U=/home/fabrice/git/pycsl-u78/scratchpad/u78; export PYTHON_CPU_COUNT=2 TMPDIR=$U/tmp
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
T=/home/fabrice/git/pycsl-u78; C=$T/test-suite/corpus/pycsl-reference; W=$U/wit/src; mkdir -p $W; cd $T || exit 2
cp $C/1054[0-5]_*.py $C/1053[257]_*.py $C/zu77a.py $C/zu78a.py $W/
echo "wit start $(date -u) $(git log --oneline -1 | cut -c1-10)"
for f in $W/1053[257]_*.py $W/1054[0-5]_*.py; do n=$(basename $f .py)
  fl=$(grep -m1 '^# pycsl-flags:' $f | sed 's/^# pycsl-flags://')
  o0=$(grep oom_kill $EV); timeout 3700 .venv/bin/python3 src/pycsl/pycsl.py $f --import-path $W $fl > $U/wit/$n.log 2>&1; rc=$?
  echo "rc=$rc flags=[$fl] tree=$T oom0=[$o0] oom1=[$(grep oom_kill $EV)]" >> $U/wit/$n.log
  echo "$n expected=$(grep -m1 -oE 'pycsl-expected: [A-Z]+' $f | cut -d' ' -f2) rc=$rc $(grep -m1 -oE 'All contracts formally proven|PYCSL-[A-Z0-9-]+|L3-tc ✗|Verification FAILED' $U/wit/$n.log)"
done
echo WDONE
