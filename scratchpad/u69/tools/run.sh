#!/bin/bash
# run.sh <mode q|p> <tree> <outdir> [listfile] : run every probe of the list (cwd = tree root unless 4th field)
# q = --no-proof --keep-mlw ; p = full proof (hoare default), PYTHON_CPU_COUNT=2, timeout 3600
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
M=$1; T=$2; O=$(realpath -m "$3"); L=${4:-/home/fabrice/git/pycsl-u69/scratchpad/u69/tools/probes.lst}
PR=/home/fabrice/git/pycsl-u69/scratchpad/u69/probes
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
export PYTHON_CPU_COUNT=2
mkdir -p "$O"
while IFS='|' read -r n x f c; do
  [ -z "$n" ] && continue
  case "$n" in \#*) continue;; esac
  ff=$PR/$f; FL=(); [ -n "$x" ] && FL=(--import-path "$(dirname "$(dirname "$ff")")/$x")
  case "$n" in r2d-dep|r2r-dep|v2down|*-noX) FL=();; esac
  if [ -n "$c" ]; then cd "$PR/$c" || exit 2; else cd "$T" || exit 2; fi
  o0=$(grep '^oom_kill ' $EV | cut -d' ' -f2); s=$(date +%s)
  if [ "$M" = q ]; then
    timeout 300 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --no-proof --keep-mlw "${FL[@]}" "$ff" > "$O/$n.log" 2>&1; rc=$?
    m="${ff%.py}.mlw"; [ -f "$m" ] && mv "$m" "$O/$n.mlw"
  else
    timeout 3600 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" "${FL[@]}" "$ff" > "$O/$n.log" 2>&1; rc=$?
  fi
  o1=$(grep '^oom_kill ' $EV | cut -d' ' -f2)
  code=$(grep -A1 "PIPELINE ERROR" "$O/$n.log" | tail -1 | sed "s|^\[[a-z-]*\] [^ ]*: ||" | cut -c1-110)
  v=$(grep -E "Verification (SUCCESS|FAIL)|All contracts|NOT a success|PIPELINE ERROR" "$O/$n.log" | head -1 | cut -c1-120)
  echo "$n rc=$rc $(( $(date +%s) - s ))s oom $o0->$o1 cwd=$(pwd) :: ${code:-no-code} :: $v"
done < "$L"
