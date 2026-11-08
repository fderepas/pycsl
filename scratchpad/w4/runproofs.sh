#!/bin/bash
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
cd /home/fabrice/git/pycsl
OUT=scratchpad/w4/proofs
for f in "$@"; do
  b=$(echo "$f" | sed 's#/#__#g; s#\.py$##')
  PYTHONHASHSEED=0 timeout 5400 python3 src/pycsl/pycsl.py "src/self-annotate/src/$f" --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' > "$OUT/$b.log" 2>&1
  echo "$?" > "$OUT/$b.rc"
done
touch "$OUT/.done_$1"
