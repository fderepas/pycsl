#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u75/scratchpad/u75/tmp; mkdir -p "$TMPDIR"
# GQ.sh <tree> <listfile of corpus-relative paths (test-suite/...py)> : --no-proof --no-typecheck per file (sweep flags), cwd = tree root; first refusal line
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
T=$1; cd $T || exit 2
while read -r f; do [ -f "$f" ] || { echo "MISSING $f"; continue; }
  fl=$(grep -m1 '^# pycsl-flags:' "$f" | cut -d: -f2-)
  out=$(timeout 300 .venv/bin/python3 src/pycsl/pycsl.py --no-proof --no-typecheck $fl "$f" 2>&1); rm -f "${f%.py}.mlw"
  m=$(echo "$out" | grep -A1 "PIPELINE ERROR" | tail -1 | cut -c1-330)
  echo "$(basename $f) :: ${m:-$(echo "$out" | grep -m1 "Verification" | cut -c1-80)}"
done < $2
