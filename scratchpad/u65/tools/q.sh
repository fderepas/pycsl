#!/bin/bash
# q.sh <tree> <outdir> [flags...] -- <file.py>... : --no-proof emission per file, cwd = tree root; keeps .mlw
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
T="$1"; O="$2"; shift 2; FL=(); while [ "$1" != "--" ]; do FL+=("$1"); shift; done; shift
mkdir -p "$O"; cd "$T" || exit 2
for f in "$@"; do
  n=$(basename "$(dirname "$f")")__$(basename "$f" .py)
  timeout 300 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --no-proof --keep-mlw "${FL[@]}" "$f" > "$O/$n.log" 2>&1
  rc=$?
  m="${f%.py}.mlw"; [ -f "$m" ] && mv "$m" "$O/$n.mlw"
  code=$(grep -o "PYCSL-[A-Z0-9-]*" "$O/$n.log" | head -1)
  msg=$(grep -A1 "PIPELINE ERROR" "$O/$n.log" | head -2 | tail -1 | cut -c1-220)
  echo "$n rc=$rc ${code:-no-code} :: ${msg:-$(tail -1 "$O/$n.log" | cut -c1-160)}"
done
