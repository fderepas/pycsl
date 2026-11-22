#!/bin/bash
# u63 type-only census of per-function vacuity probes built by THIS tree's _run_vacuity_gate:
# mirror (53) + corpus root (3325) + pyref (2185) emissions of v74 (emission == L18). 4 parallel chunks.
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHON_CPU_COUNT=2
U=/home/fabrice/git/pycsl-u63; O=$U/scratchpad/u63/census; V=/home/fabrice/git/pycsl/scratchpad/run8/v74
mkdir -p $O; cd $U
{ ls $V/mir-int/*.mlw; ls $V/bd-int/*.mlw; ls $V/bd-int/pyref/*.mlw; } > $O/all.txt
split -n l/3 -d $O/all.txt $O/chunk.
for c in $O/chunk.0*; do .venv/bin/python scratchpad/u62/pfcensus.py $U $c.tsv $(cat $c) > $c.log 2>&1 & done
wait; echo "census done $(date -u)" >> $O/done.txt
