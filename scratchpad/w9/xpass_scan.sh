#!/bin/bash
# Which `pycsl-expected: FAIL` tests actually PROVE today? Each such test is a negative
# witness the suite currently reports as PASS.
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
one() {
  f="$1"
  fl=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  out=$(timeout 300 /home/fabrice/git/pycsl/.venv/bin/python3 \
        /home/fabrice/git/pycsl/src/pycsl/pycsl.py $fl "$f" 2>&1)
  if echo "$out" | grep -q 'Verification SUCCESS'; then echo "XPASS  $f"; fi
}
export -f one
grep -rl '^# pycsl-expected: FAIL' test-suite/corpus/ | sort | \
  xargs -P 6 -I{} bash -c 'one "$@"' _ {} > scratchpad/w9/xpass.txt
echo DONE >> scratchpad/w9/xpass.txt
