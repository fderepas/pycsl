#!/bin/bash
# wit.sh <mode q|p> <tree> <outdir> : run the u66 corpus witnesses + helpers of the u66 tree with <tree>'s
# pycsl, flags from each file's `# pycsl-flags:` header, cwd = the u66 tree root (paths relative)
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
M=$1; T=$2; O=$(realpath -m "$3"); W=/home/fabrice/git/pycsl-u66; C=test-suite/corpus/pycsl-reference
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
mkdir -p $O; cd $W || exit 2
for f in $C/1038[0-3]_*.py $C/zr80/*.py $C/zr81/*.py $C/zq80.py $C/zq80/*.py $C/zh80/*.py $(find $C/multi_file_lib/u66 -name '*.py' | sort); do
  n=$(echo "${f#$C/}" | tr '/' '_' ); FL=($(grep -m1 '^# pycsl-flags:' $f | cut -d: -f2-))
  o0=$(grep '^oom_kill ' $EV | cut -d' ' -f2); s=$(date +%s)
  if [ "$M" = q ]; then timeout 300 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py --no-proof "${FL[@]}" $f > $O/$n.log 2>&1; rc=$?
  else timeout 3600 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py "${FL[@]}" $f > $O/$n.log 2>&1; rc=$?; fi
  o1=$(grep '^oom_kill ' $EV | cut -d' ' -f2)
  hdr=$(grep -m1 -o 'pycsl-expected: [A-Z]*' $f | cut -d' ' -f2)
  v=$(grep -E "Verification SUCCESS|Verification FAIL|NOT a success|PIPELINE ERROR" $O/$n.log | head -1 | cut -c1-90)
  msg=$(grep -A1 "PIPELINE ERROR" $O/$n.log | tail -1 | sed "s|^\[[a-z-]*\] [^ ]*: ||" | cut -c1-120)
  echo "$n hdr=${hdr:-none} rc=$rc $(( $(date +%s)-s ))s oom $o0->$o1 :: $v :: $msg"
done
