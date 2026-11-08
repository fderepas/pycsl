#!/bin/bash
# prove_one.sh <file> <timeout> <tag>
f="$1"; TO="$2"; tag="$3"
ROOT="/home/fabrice.derepas@canonical.com/git/pycsl"
cd "$ROOT"
rm -f "scratchpad/nt/${tag}.done" "scratchpad/nt/${tag}.log"
timeout "$TO" .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl > "scratchpad/nt/${tag}.log" 2>&1
ec=$?
if grep -q "Verification SUCCESS" "scratchpad/nt/${tag}.log"; then
  echo "VALID ec=$ec" > "scratchpad/nt/${tag}.done"
else
  echo "NONVALID ec=$ec" > "scratchpad/nt/${tag}.done"
fi
