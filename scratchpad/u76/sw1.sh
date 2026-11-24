#!/bin/bash
# sw1.sh: base sweep (pycsl-u76b, ba48d5888 = L21) then head sweep (pycsl-u76h, snapshot) + compares. cwd = each tree root.
U=/home/fabrice/git/pycsl-u76/scratchpad/u76; HT=${HT:-/home/fabrice/git/pycsl-u76h}; HS=${HS:-$U/sw/head1}
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=$U/tmp
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
if [ ! -f $U/sw/base/done.txt ]; then
  B=$U/sw/base; mkdir -p $B; cd /home/fabrice/git/pycsl-u76b || exit 2
  echo "base start $(date -u) $(git log --oneline -1 | cut -c1-12) $(grep oom_kill $EV)"
  bin/byte-diff-sweep.sh $B/bd > $B/bd.log 2>&1; echo "base bd rc=$? $(tail -2 $B/bd.log | tr '\n' ' ')"
  bin/mirror-emit-sweep.sh $B/mir > $B/mir.log 2>&1; echo "base mir rc=$? $(tail -1 $B/mir.log)"
  echo "base done $(date -u)" > $B/done.txt
fi
mkdir -p $HS; cd $HT || exit 2
echo "head start $(date -u) $(git log --oneline -1 | cut -c1-12) $(grep oom_kill $EV)"
bin/byte-diff-sweep.sh $HS/bd > $HS/bd.log 2>&1; echo "head bd rc=$? $(tail -2 $HS/bd.log | tr '\n' ' ')"
bin/mirror-emit-sweep.sh $HS/mir > $HS/mir.log 2>&1; echo "head mir rc=$? $(tail -1 $HS/mir.log)"
python3 bin/byte-diff-compare.py $U/sw/base/bd $HS/bd > $HS/C-root.txt 2>&1; echo "compare root rc=$? $(tail -3 $HS/C-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $U/sw/base/bd/pyref $HS/bd/pyref --min-files 2000 > $HS/C-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -3 $HS/C-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $U/sw/base/mir $HS/mir --min-files 45 > $HS/C-mir.txt 2>&1; echo "compare mir rc=$? $(tail -3 $HS/C-mir.txt | tr '\n' ' ')"
diff -rq $U/sw/base/mir $HS/mir > $HS/diffrq-mir.txt 2>&1; echo "diff -rq mir rc=$? $(wc -l < $HS/diffrq-mir.txt) lines"
echo "sw end $(date -u) $(grep oom_kill $EV)"
