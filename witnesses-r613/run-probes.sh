#!/bin/bash
# run-probes.sh <tree> <outdir> <probe-dir>... : pycsl verdict of each probe x3 memory models,
# cwd = the tree root (rule 28).
T="$1"; O="$2"; shift 2
mkdir -p "$O"; cd "$T" || exit 2
for d in "$@"; do
  n=$(basename "$d")
  for mm in hoare typed store; do
    timeout 900 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --memory-model $mm "$d/prog.py" > "$O/$n.$mm.log" 2>&1
    rc=$?
    v=$(grep -E "PROVED|VERIFY|FAIL|REFUS|PYCSL-[A-Z0-9-]+|Error" "$O/$n.$mm.log" | tail -2 | tr '\n' ' ' | cut -c1-220)
    echo "$n $mm rc=$rc $v" | tee -a "$O/summary.txt"
  done
done
