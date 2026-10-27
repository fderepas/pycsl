#!/bin/bash
# libscreen.sh <tree> <out.tsv> : --no-proof (type-checked) rc of every src/pycsl_lib file
T=$1; O=$2
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
cd "$T" || exit 2
: > "$O"
one() { T=$1; f=$2; out=$(cd "$T" && PYTHONHASHSEED=0 timeout 600 .venv/bin/python3 src/pycsl/pycsl.py --no-proof --import-path src/pycsl_lib --import-path "$(dirname "$f")" "$f" 2>&1); rc=$?; msg=$(printf '%s\n' "$out" | grep -m1 -E "PYCSL-|UB-|\[whyml\]|\[ir-semantic\]|rror" | cut -c1-160); rm -f "${f%.py}.mlw"; printf '%s\t%s\t%s\n' "$f" "$rc" "$msg"; }
export -f one
find src/pycsl_lib -name '*.py' | sort | xargs -P 6 -I{} bash -c 'one "$@"' _ "$T" {} | sort > "$O"
echo "lib screen: $(wc -l < "$O") files, rc0=$(awk -F'\t' '$2==0' "$O" | wc -l)"
