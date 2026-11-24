#!/bin/bash
# wit.sh <mode q|p> <tree> <outdir> : the u71 corpus witnesses 10435-10440 + helpers, with <tree>'s pycsl, flags from
# each file's `# pycsl-flags:` header, cwd = the u71 tree root (relative paths, as the corpus runs them)
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
M=$1; T=$2; O=$(realpath -m "$3"); W=/home/fabrice/git/pycsl-u71; C=test-suite/corpus/pycsl-reference
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
mkdir -p $O; cd $W || exit 2
for f in $C/1043[5-9]_*.py $C/10440_*.py $C/zh3[5-7].py $C/zd3[5-7].py $C/zp35/*.py $C/zp36/*.py $C/zp36/sub/*.py \
         $C/zp37/*.py $C/multi_file_lib/u71y/zh38.py $C/zp39/*.py $C/zp40/*.py; do
  [ -f "$f" ] || { echo "MISSING $f"; continue; }
  n=$(echo "${f#$C/}" | tr '/' '_' ); FL=($(grep -m1 '^# pycsl-flags:' $f | cut -d: -f2-))
  o0=$(grep '^oom_kill ' $EV | cut -d' ' -f2); s=$(date +%s)
  if [ "$M" = q ]; then timeout 300 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py --no-proof "${FL[@]}" $f > $O/$n.log 2>&1; rc=$?
  else timeout 3600 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py "${FL[@]}" $f > $O/$n.log 2>&1; rc=$?; fi
  o1=$(grep '^oom_kill ' $EV | cut -d' ' -f2)
  hdr=$(grep -m1 -o 'pycsl-expected: [A-Z]*' $f | cut -d' ' -f2)
  code=$(grep -o "PYCSL-[A-Z0-9-]*" $O/$n.log | head -1)
  v=$(grep -E "Verification SUCCESS|Verification FAIL|NOT a success|PIPELINE ERROR" $O/$n.log | head -1 | cut -c1-90)
  msg=$(grep -A1 "PIPELINE ERROR" $O/$n.log | tail -1 | sed "s|^\[[a-z-]*\] [^ ]*: ||" | cut -c1-120)
  echo "$n hdr=${hdr:-none} rc=$rc $(( $(date +%s)-s ))s oom $o0->$o1 :: ${code:-no-code} :: $v :: $msg"
done
