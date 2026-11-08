#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
: > scratchpad/w9/rem30_bothprovers.txt
one() {
  n="$1"; suite="${n%%/*}"; name="${n#*/}"
  for f in $(find "test-suite/corpus/$suite" -name "$name.py" | sort); do
    fl=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
    out=$(timeout 400 /home/fabrice/git/pycsl/.venv/bin/python3 \
          /home/fabrice/git/pycsl/src/pycsl/pycsl.py --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' $fl "$f" 2>&1)
    if echo "$out" | grep -q 'Verification SUCCESS'; then printf 'NOW-PASSES\t%s\n' "$f"
    else printf 'still-fails\t%s\n' "$f"; fi
  done
}
export -f one
xargs -a scratchpad/w9/rem30.txt -P 5 -I{} bash -c 'one "$@"' _ {} >> scratchpad/w9/rem30_bothprovers.txt
echo DONE >> scratchpad/w9/rem30_bothprovers.txt
