#!/bin/bash
# libscreen.sh <tree> <out.tsv> : --no-proof screen of every src/pycsl_lib module (rc, first PYCSL code).
# Run AS a heavy.sh command. Columns as g3's lib-base.tsv: path, rc, code.
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
T=$1; O=$2; cd "$T"; : > "$O.tmp"
one() { T=$1; f=$2; o=$(cd "$T" && PYTHONHASHSEED=0 timeout 300 .venv/bin/python3 src/pycsl/pycsl.py --no-proof "$f" 2>&1); rc=$?
  printf '%s\t%s\t%s\n' "$f" "$rc" "$(printf '%s' "$o" | grep -oE 'PYCSL-[A-Z0-9-]+' | head -1)"; }
export -f one
find src/pycsl_lib -name '*.py' | sort | xargs -P 6 -I{} bash -c 'one "$@"' _ "$T" {} >> "$O.tmp"
sort "$O.tmp" > "$O"; rm -f "$O.tmp"; echo "files=$(wc -l < "$O") rc0=$(awk -F'\t' '$2==0' "$O" | wc -l)"
