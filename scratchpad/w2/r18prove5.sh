#!/bin/bash
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad
export PYTHONHASHSEED=0
cd /home/fabrice/git/pycsl
OUT=scratchpad/w2/r18proofs5
mkdir -p "$OUT"
for f in "$@"; do
  key=$(echo "$f" | tr '/' '_')
  python3 -u src/pycsl/pycsl.py "$f" --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' > "$OUT/$key.log" 2>&1
  if grep -q "Verification SUCCESS" "$OUT/$key.log"; then
      echo "OK   $f  ($(grep -c 'Prover result' "$OUT/$key.log") goals)" >> "$OUT/RESULTS"
  else
      echo "FAIL $f" >> "$OUT/RESULTS"
  fi
done
echo "ALLDONE" >> "$OUT/RESULTS"
