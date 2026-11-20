#!/bin/bash
# type-only census of call-site probes on the 8 already-emitted mlw, base rewriter vs head rewriter
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
U=/home/fabrice/git/pycsl-u56; cd $U || exit 2
export PYTHON_CPU_COUNT=4
for t in head base; do
  T=$U; [ $t = base ] && T=/home/fabrice/git/pycsl-u56-base
  echo "== $t ($T) $(date -u)"
  PYTHONHASHSEED=0 timeout 3000 .venv/bin/python3 -W ignore scratchpad/u56/census.py $T scratchpad/u56/census8-$t.tsv scratchpad/u56/emit/*.mlw 2>&1 | grep -v '^\[\*\]'
done
