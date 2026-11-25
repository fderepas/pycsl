#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u73/scratchpad/u73/tmp; mkdir -p "$TMPDIR"
# D.sh <mode q|p> <tree> <outdir> <probe-dir-rel>... : probe dirs (relative to u73/probes) holding P/prog.py,
# optional `flags` (one arg per line, @P = probe dir; an empty line is an empty arg) and `cwd` (relative to the
# probe dir; default the tree root). q = --no-proof --keep-mlw ; p = full proof, hoare default, PYTHON_CPU_COUNT=2,
# timeout 3600. One line per probe.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
M=$1; T=$2; O=$(realpath -m "$3"); shift 3
PR=/home/fabrice/git/pycsl-u73/scratchpad/u73/probes
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
export PYTHON_CPU_COUNT=2
mkdir -p "$O"
for k in "$@"; do
  P=$PR/$k; ff=$P/P/prog.py; [ -f "$ff" ] || { echo "$k MISSING $ff"; continue; }
  FL=(); [ -f $P/flags ] && while IFS= read -r l; do FL+=("${l//@P/$P}"); done < $P/flags
  if [ -f $P/cwd ]; then cd "$P/$(cat $P/cwd)" || exit 2; else cd "$T" || exit 2; fi
  n=${k//\//_}
  o0=$(grep '^oom_kill ' $EV | cut -d' ' -f2); s=$(date +%s)
  if [ "$M" = q ]; then
    timeout 300 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --no-proof --keep-mlw "${FL[@]}" "$ff" > "$O/$n.log" 2>&1; rc=$?
    m="${ff%.py}.mlw"; [ -f "$m" ] && mv "$m" "$O/$n.mlw"
  else
    timeout 3600 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" "${FL[@]}" "$ff" > "$O/$n.log" 2>&1; rc=$?
    m="${ff%.py}.mlw"; [ -f "$m" ] && rm -f "$m"
  fi
  o1=$(grep '^oom_kill ' $EV | cut -d' ' -f2)
  code=$(grep -o "PYCSL-[A-Z0-9-]*" "$O/$n.log" | head -1)
  msg=$(grep -A1 "PIPELINE ERROR" "$O/$n.log" | tail -1 | sed "s|^\[[a-z-]*\] [^ ]*: ||" | cut -c1-110)
  v=$(grep -E "Verification (SUCCESS|FAIL)|All contracts|NOT a success|PIPELINE ERROR" "$O/$n.log" | head -1 | cut -c1-100)
  echo "$k rc=$rc $(( $(date +%s) - s ))s oom $o0->$o1 :: ${code:-no-code} :: $v :: ${msg}"
done
