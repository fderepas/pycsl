#!/bin/bash
# wit.sh <mode q|p> <tree> <outdir> [witness-tree] : the u70 corpus witnesses + helpers of <witness-tree>
# (default the h1 snapshot) with <tree>'s pycsl, flags from `# pycsl-flags:`, cwd = witness-tree root
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
M=$1; T=$2; O=$(realpath -m "$3"); W=${4:-/home/fabrice/git/pycsl-u70-h1}; C=test-suite/corpus/pycsl-reference
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
mkdir -p $O; cd $W || exit 2
echo "## wit $M $T $(git -C $T rev-parse --short HEAD) files of $W $(git rev-parse --short HEAD) $(date -u)"
for f in $C/1042[0-7]_*.py $C/qa70.py $C/qb70.py; do
  n=$(basename $f .py); FL=($(grep -m1 '^# pycsl-flags:' $f | cut -d: -f2-))
  o0=$(grep '^oom_kill ' $EV | cut -d' ' -f2); s=$(date +%s)
  if [ "$M" = q ]; then timeout 300 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py --no-proof "${FL[@]}" $f > $O/$n.log 2>&1; rc=$?
  else timeout 3600 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py "${FL[@]}" $f > $O/$n.log 2>&1; rc=$?; fi
  o1=$(grep '^oom_kill ' $EV | cut -d' ' -f2)
  hdr=$(grep -m1 -o 'pycsl-expected: [A-Z]*' $f | cut -d' ' -f2)
  v=$(grep -E "Verification SUCCESS|Verification FAIL|NOT a success|PIPELINE ERROR" $O/$n.log | head -1 | cut -c1-90)
  msg=$(grep -A1 "PIPELINE ERROR" $O/$n.log | tail -1 | sed "s|^\[[a-z-]*\] [^ ]*: ||" | cut -c1-120)
  echo "$n hdr=${hdr:-none} rc=$rc $(( $(date +%s)-s ))s oom $o0->$o1 :: $v :: $msg"
done
echo "## end $(date -u)"
