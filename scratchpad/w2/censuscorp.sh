#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
one() {
  f="$1"
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  PYCSL_CENSUS_FILE="$f" PYTHONHASHSEED=0 /home/fabrice/git/pycsl/.venv/bin/python3 /home/fabrice/git/pycsl/src/pycsl/pycsl.py --no-proof --no-typecheck $flags "$f" 2>&1 >/dev/null | grep UNIONARMDECLINE
}
export -f one
ls test-suite/corpus/pycsl-reference/0*.py | xargs -P 8 -I{} bash -c 'one "$@"' _ {} > scratchpad/w2/census_arm_corpus.txt
echo CENSUSDONE
