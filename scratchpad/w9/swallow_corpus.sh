#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
: > scratchpad/w9/swallow_corpus.txt
run_one() {
  f="$1"
  timeout 120 /home/fabrice/git/pycsl/.venv/bin/python3 scratchpad/w9/swallow_probe.py /home/fabrice/git/pycsl "$f" 2>&1 >/dev/null | grep '^SWALLOW'
}
export -f run_one
find test-suite/corpus/pycsl-reference -name '0*.py' | sort | xargs -P 6 -I{} bash -c 'run_one "$@"' _ {} >> scratchpad/w9/swallow_corpus.txt
echo DONE >> scratchpad/w9/swallow_corpus.txt
