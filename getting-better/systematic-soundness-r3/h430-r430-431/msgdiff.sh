#!/bin/bash
# msgdiff.sh <tree> <out.tsv> <list> : --no-proof run of each listed corpus witness (its pycsl-flags),
# one row: basename, first line after "PIPELINE ERROR" (or "-"). Run AS a heavy.sh command.
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
T=$1; O=$2; L=$3; cd "$T"
one() { T=$1; b=$2; f="$T/test-suite/corpus/pycsl-reference/$b"
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  o=$(cd "$T" && PYTHONHASHSEED=0 timeout 300 .venv/bin/python3 src/pycsl/pycsl.py --no-proof $flags "$f" 2>&1)
  m=$(printf '%s\n' "$o" | grep -A1 'PIPELINE ERROR' | sed -n 2p | tr '\t' ' ' | cut -c1-300)
  printf '%s\t%s\n' "$b" "${m:--}"; }
export -f one
xargs -P 6 -I{} bash -c 'one "$@"' _ "$T" {} < "$L" | sort > "$O"; wc -l < "$O"
