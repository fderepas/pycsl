#!/bin/bash
WT=/home/fabrice/git/pycsl/scratchpad/w3/wt
OUT=/home/fabrice/git/pycsl/scratchpad/w3/census19b
mkdir -p "$OUT"
cd "$WT"
for rel in $(cd src/self-annotate/src && find . -name '*.py' | sed 's|^\./||' | sort); do
  timeout 300 python3 /home/fabrice/git/pycsl/scratchpad/w3/probe_all4.py "$WT" "$rel" "$OUT" 2>&1 | tail -2
done
echo CENSUSDONE
