#!/bin/bash
# p.sh <tree> <outdir> [flags...] -- <file.py>... : full pycsl proof per file, cwd = tree root, PYTHON_CPU_COUNT=2
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PYTHON_CPU_COUNT=2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
T="$1"; O="$2"; shift 2; FL=(); while [ "$1" != "--" ]; do FL+=("$1"); shift; done; shift
mkdir -p "$O"; cd "$T" || exit 2
for f in "$@"; do
  n=$(basename "$(dirname "$f")")__$(basename "$f" .py)
  o0=$(grep '^oom_kill ' $EV | cut -d' ' -f2)
  s=$(date +%s)
  timeout 3600 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" "${FL[@]}" "$f" > "$O/$n.log" 2>&1
  rc=$?
  o1=$(grep '^oom_kill ' $EV | cut -d' ' -f2)
  v=$(grep -E "Verification (SUCCESS|FAIL)|All contracts|PYCSL-[A-Z0-9-]+|NOT a success" "$O/$n.log" | head -2 | tr '\n' ' ' | cut -c1-200)
  echo "$n rc=$rc $(( $(date +%s) - s ))s oom $o0->$o1 :: $v"
done
