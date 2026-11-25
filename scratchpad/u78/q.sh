#!/bin/bash
# q.sh: QUICK --no-proof of witnesses 10540-10545 and rt88 probes f23 / f23x owner / f19 owner, head (pycsl-u78) and base (pycsl-u78b @ run9-u77); cwd = tree root
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
U=/home/fabrice/git/pycsl-u78/scratchpad/u78; export PYTHON_CPU_COUNT=2 TMPDIR=$U/tmp
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
C=/home/fabrice/git/pycsl-u78/test-suite/corpus/pycsl-reference; R=/home/fabrice/git/pycsl/scratchpad/rt88/c
W=$U/q/src; mkdir -p $W; cp $C/1054[0-5]_*.py $C/zu78a.py $R/f23/o88f23.py $R/f23x/o88f23x.py $R/f19/o88f19.py $W/
for a in h:/home/fabrice/git/pycsl-u78 b:/home/fabrice/git/pycsl-u78b; do tag=${a%%:*}; T=${a#*:}; cd $T || exit 2; mkdir -p $U/q/$tag
  for f in $W/1054*.py $W/o88*.py; do n=$(basename $f .py)
    o0=$(grep oom_kill $EV); timeout 1200 .venv/bin/python3 src/pycsl/pycsl.py $f --import-path $W --no-proof > $U/q/$tag/$n.log 2>&1; rc=$?
    echo "rc=$rc tree=$T oom0=[$o0] oom1=[$(grep oom_kill $EV)]" >> $U/q/$tag/$n.log
    echo "$tag $n rc=$rc $(grep -m1 -oE 'PYCSL-[A-Z0-9-]+[^`]*`[^`]*`[^`]*`[a-z_]*`|L3-tc[^\n]{0,60}' $U/q/$tag/$n.log | head -1)"
  done; done
echo QDONE
