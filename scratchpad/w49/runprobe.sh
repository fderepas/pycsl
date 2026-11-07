#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
for f in "$@"; do
  out=$(PYTHONHASHSEED=0 timeout 300 python3 src/pycsl/pycsl.py "$f" 2>&1)
  rc=$?
  if echo "$out" | grep -q "All contracts formally proven\|Verification SUCCESS"; then v=PROVED
  elif echo "$out" | grep -qi "not supported\|unsupported\|refus\|Error"; then v=REFUSED/ERROR
  else v=FAILED; fi
  echo "== $(basename $f): $v (rc=$rc)"
  echo "$out" | tail -3 | sed 's/^/   /'
done
