#!/bin/bash
# batch.sh <tree> <outdir> <models...> : prove each probe in p/ (or $PROBES) under each model
T=$1; O=$2; shift 2
mkdir -p "$O"
cd /home/fabrice/git/pycsl/scratchpad/u28/${PROBES:-p}
for f in ${FILES:-*.py}; do
  for m in "$@"; do
    timeout 300 $T/.venv/bin/python $T/src/pycsl/pycsl.py --memory-model $m "$f" > "$O/${f%.py}.$m.out" 2>&1
    rc=$?
    v=$(grep -E "Verification (SUCCESS|FAILED)|PYCSL-[A-Z0-9-]+|Error" "$O/${f%.py}.$m.out" | head -1 | cut -c1-140)
    echo "$f $m rc=$rc $v"
  done
done
