#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/w7/tmp
ok=0; bad=""
while read n; do
  f="test-suite/corpus/pycsl-reference/$n.py"; [ -f "$f" ] || continue
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  xf=$(grep -m1 '^# pycsl-expected: FAIL' "$f" 2>/dev/null)
  out=$(PYTHONHASHSEED=0 timeout 400 python3 src/pycsl/pycsl.py $flags "$f" 2>&1)
  if echo "$out" | grep -q "Verification SUCCESS"; then ok=$((ok+1));
  elif [ -n "$xf" ]; then ok=$((ok+1));
  else bad="$bad $n"; fi
done < /home/fabrice/git/pycsl/scratchpad/w7/changed_arr.txt
echo "ARR PROVE OK: $ok"
echo "ARR PROVE FAIL:$bad"
