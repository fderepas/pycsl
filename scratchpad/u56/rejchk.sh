#!/bin/bash
# type-only check of the ORIGINAL emissions whose call-site probe head rejects, + base-rewriter census of them
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
U=/home/fabrice/git/pycsl-u56; cd $U || exit 2
while read f; do
  r=$(why3 prove --type-only "$f" 2>&1 | grep -v '^Warning' | tr '\n' ' ' | cut -c1-200); echo "$(basename $f) orig-type-only: rc=${PIPESTATUS[0]} ${r}"
done < scratchpad/u56/census/rej.list
PYTHONHASHSEED=0 .venv/bin/python3 -W ignore scratchpad/u56/census.py /home/fabrice/git/pycsl-u56-base scratchpad/u56/census/base-rej.tsv scratchpad/u56/census/rej.list 2>&1 | grep -v '^\[\*\]' | tail -3
