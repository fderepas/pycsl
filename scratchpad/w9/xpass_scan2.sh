#!/bin/bash
# Same scan, but with BOTH provers actually present (the config asks for Alt-Ergo 2.6.2,
# which does not exist in this switch, so a default run silently uses Z3 alone).
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
one() {
  f="$1"
  fl=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  out=$(timeout 300 /home/fabrice/git/pycsl/.venv/bin/python3 \
        /home/fabrice/git/pycsl/src/pycsl/pycsl.py --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' $fl "$f" 2>&1)
  if echo "$out" | grep -q 'Verification SUCCESS'; then echo "XPASS  $f"; fi
}
export -f one
grep -rl '^# pycsl-expected: FAIL' test-suite/corpus/ | sort | \
  xargs -P 6 -I{} bash -c 'one "$@"' _ {} > scratchpad/w9/xpass2.txt
echo DONE >> scratchpad/w9/xpass2.txt
