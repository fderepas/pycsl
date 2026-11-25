#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u75/scratchpad/u75/tmp; mkdir -p "$TMPDIR"
# wit.sh <mode q|p> <tree> <outdir> [witness-tree] : u75 witnesses 10490-10500 + helpers, run with <tree>'s pycsl,
# flags from `# pycsl-flags:`, cwd = the witness tree root (default the u73 h1 snapshot; relative paths as the corpus)
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
M=$1; T=$2; O=$(realpath -m "$3"); W=${4:-/home/fabrice/git/pycsl-u75}; C=test-suite/corpus/pycsl-reference
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
mkdir -p $O; cd $W || exit 2
for f in $C/1049[0-9]_*.py $C/10500_*.py $C/zu75*.py $C/zu75*/*.py; do
  [ -f "$f" ] || { echo "MISSING $f"; continue; }
  n=$(echo "${f#$C/}" | tr '/' '_' ); FL=($(grep -m1 '^# pycsl-flags:' $f | cut -d: -f2-))
  o0=$(grep '^oom_kill ' $EV | cut -d' ' -f2); s=$(date +%s)
  if [ "$M" = q ]; then timeout 300 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py --no-proof "${FL[@]}" $f > $O/$n.log 2>&1; rc=$?
  else timeout 3600 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py "${FL[@]}" $f > $O/$n.log 2>&1; rc=$?; fi
  rm -f "${f%.py}.mlw"
  o1=$(grep '^oom_kill ' $EV | cut -d' ' -f2)
  hdr=$(grep -m1 -o 'pycsl-expected: [A-Z]*' $f | cut -d' ' -f2)
  v=$(grep -E "Verification SUCCESS|Verification FAIL|NOT a success|PIPELINE ERROR" $O/$n.log | head -1 | cut -c1-90)
  msg=$(grep -A1 "PIPELINE ERROR" $O/$n.log | tail -1 | sed "s|^\[[a-z-]*\] [^ ]*: ||" | cut -c1-120)
  echo "$n hdr=${hdr:-none} rc=$rc $(( $(date +%s)-s ))s oom $o0->$o1 :: $v :: $msg"
done
