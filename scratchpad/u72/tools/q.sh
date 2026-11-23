#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u72/scratchpad/u72/tmp; mkdir -p $TMPDIR
# q.sh <tree> <outdir> -- <file.py>... : --no-proof --keep-mlw emission per file, cwd = tree root
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PYTHON_CPU_COUNT=2
T="$1"; O="$2"; shift 2; FL=(); while [ "$1" != "--" ]; do FL+=("$1"); shift; done; shift
mkdir -p "$O"; cd "$T" || exit 2
for f in "$@"; do
  n=$(basename "$f" .py)
  timeout 300 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --no-proof --keep-mlw "${FL[@]}" "$f" > "$O/$n.log" 2>&1
  rc=$?
  m="${f%.py}.mlw"; [ -f "$m" ] && mv "$m" "$O/$n.mlw"
  code=$(grep -o "PYCSL-[A-Z0-9-]*" "$O/$n.log" | head -1)
  msg=$(grep -iE -A1 "PIPELINE ERROR|error" "$O/$n.log" | head -2 | tr '\n' ' ' | cut -c1-240)
  echo "$n rc=$rc ${code:-no-code} :: ${msg:-$(tail -1 "$O/$n.log" | cut -c1-160)}"
done
