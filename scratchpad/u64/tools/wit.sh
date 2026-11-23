#!/bin/bash
# wit.sh <code-tree> <outdir> <q|p> [files...] : run <code-tree>'s pycsl on the u64 witnesses (files live in
# the u64 tree; cwd = the u64 tree root, so --import-path flags resolve there). q = --no-proof, p = full proof.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PYTHON_CPU_COUNT=2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
T=$1; O=$2; M=$3; shift 3; W=/home/fabrice/git/pycsl-u64; mkdir -p "$O"; cd $W || exit 2
FILES=("$@"); [ ${#FILES[@]} -eq 0 ] && FILES=($(ls test-suite/corpus/pycsl-reference/1034[0-9]_*.py))
for f in "${FILES[@]}"; do
  n=$(basename "$f" .py); fl=$(grep -m1 '^# pycsl-flags:' "$f" | sed 's/^# pycsl-flags://')
  o0=$(grep '^oom_kill ' $EV 2>/dev/null | cut -d' ' -f2); s=$(date +%s)
  if [ "$M" = q ]; then timeout 300 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --no-proof $fl "$f" > "$O/$n.log" 2>&1
  else timeout 1500 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" $fl "$f" > "$O/$n.log" 2>&1; fi
  rc=$?; o1=$(grep '^oom_kill ' $EV 2>/dev/null | cut -d' ' -f2)
  v=$(grep -E "Verification (SUCCESS|FAIL)|PYCSL-[A-Z0-9-]+|PIPELINE ERROR" "$O/$n.log" | head -2 | tr '\n' ' ' | cut -c1-160)
  echo "$n rc=$rc $(( $(date +%s) - s ))s oom $o0->$o1 :: $v"
done
