#!/bin/bash
# run.sh <mode q|p> <tree> <outdir> [listfile] : every probe of the list with <tree>'s pycsl, cwd = <tree> root
# q = --no-proof --keep-mlw ; p = full proof, PYTHON_CPU_COUNT=2, timeout 3600
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
M=$1; T=$2; O=$(realpath -m "$3"); L=${4:-/home/fabrice/git/pycsl-u70/scratchpad/u70/tools/p.lst}
PR=/home/fabrice/git/pycsl-u70/scratchpad/u70/probes
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
export PYTHON_CPU_COUNT=2; mkdir -p "$O"; cd "$T" || exit 2
echo "## $M $T $(git rev-parse --short HEAD) $(date -u) $(grep oom_kill $EV)"
while IFS='|' read -r n f; do
  [ -z "$n" ] && continue; case "$n" in \#*) continue;; esac
  ff=$PR/$f; o0=$(grep '^oom_kill ' $EV | cut -d' ' -f2); s=$(date +%s)
  if [ "$M" = q ]; then
    timeout 300 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --no-proof --keep-mlw "$ff" > "$O/$n.log" 2>&1; rc=$?
    m="${ff%.py}.mlw"; [ -f "$m" ] && mv "$m" "$O/$n.mlw"
  else
    timeout 3600 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" "$ff" > "$O/$n.log" 2>&1; rc=$?
  fi
  o1=$(grep '^oom_kill ' $EV | cut -d' ' -f2)
  code=$(grep -A1 "PIPELINE ERROR" "$O/$n.log" | tail -1 | sed "s|^\[[a-z-]*\] [^ ]*: ||" | cut -c1-110)
  v=$(grep -E "Verification (SUCCESS|FAIL)|All contracts|NOT a success|PIPELINE ERROR" "$O/$n.log" | head -1 | cut -c1-120)
  echo "$n rc=$rc $(( $(date +%s) - s ))s oom $o0->$o1 :: ${code:-no-code} :: $v"
done < "$L"
echo "## end $(date -u)"
