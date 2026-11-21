#!/bin/bash
# codescr.sh <tree> <out.tsv> <listfile> --no-proof : run AS heavy.sh (QUICK class).
# --no-proof --no-typecheck run of each listed file; row: basename, first line after PIPELINE ERROR (or -)
T=$1; O=$2; L=$3
one() { T=$1; f=$2
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  o=$(cd "$T" && PYTHONHASHSEED=0 timeout 300 .venv/bin/python3 src/pycsl/pycsl.py --no-proof --no-typecheck $flags --import-path "$(dirname "$f")" --import-path src/pycsl "$f" 2>&1)
  m=$(printf '%s\n' "$o" | grep -A1 'PIPELINE ERROR' | sed -n 2p | tr '\t' ' ' | cut -c1-220)
  printf '%s\t%s\n' "$(basename "$f")" "${m:--}"; }
export -f one
xargs -P 4 -I{} bash -c 'one "$@"' _ "$T" {} < "$L" | sort > "$O"; wc -l < "$O"; echo DONE
