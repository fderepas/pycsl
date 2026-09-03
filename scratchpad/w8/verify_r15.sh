#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/w7/tmp
ok=0; bad=""
while read n; do
  n="${n%.mlw}"
  f="test-suite/corpus/pycsl-reference/$n.py"; [ -f "$f" ] || { bad="$bad MISSING:$n"; continue; }
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  xf=$(grep -m1 '^# pycsl-expected: FAIL' "$f" 2>/dev/null)
  out=$(PYTHONHASHSEED=0 timeout 900 python3 src/pycsl/pycsl.py $flags "$f" 2>&1)
  if echo "$out" | grep -q "Verification SUCCESS"; then ok=$((ok+1));
  elif [ -n "$xf" ]; then ok=$((ok+1));
  else bad="$bad $n"; fi
done < /home/fabrice/git/pycsl/scratchpad/w8/changed_r15.txt
echo "R15 CORPUS PROVE OK: $ok / 12"
echo "R15 CORPUS FAIL:$bad"
