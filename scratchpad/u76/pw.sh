#!/bin/bash
# pw.sh [tree]: FULL proofs of the u76 corpus witnesses 10510-10525 from the tree root (default: the worktree)
T=${1:-/home/fabrice/git/pycsl-u76}; U=/home/fabrice/git/pycsl-u76/scratchpad/u76; O=$U/wit/$(basename $T); mkdir -p $O
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=$U/tmp
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
cd $T || exit 2
for f in test-suite/corpus/pycsl-reference/105[12][0-9]_*.py; do n=$(basename ${f%.py}); o0=$(grep oom_kill $EV)
  fl=$(grep -m1 '^# pycsl-flags:' $f | cut -d: -f2-)
  timeout 3700 .venv/bin/python3 src/pycsl/pycsl.py $fl $f > $O/$n.log 2>&1; rc=$?
  v=$(grep -m1 -oE "All contracts formally proven|PIPELINE ERROR|Verification FAILED|Verification SUCCESS" $O/$n.log)
  c=$(grep -m1 -oE "PYCSL-[A-Z0-9-]+" $O/$n.log); echo "$n expected=$(grep -m1 -oE 'pycsl-expected: [A-Z]+' $f | cut -d' ' -f2) rc=$rc $v $c [$o0 / $(grep oom_kill $EV)]"
done
