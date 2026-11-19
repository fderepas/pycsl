#!/bin/bash
# job2: type-only census of every call-site probe body over the full mirror + corpus root + pyref emissions (base sweep), head then base rewriter
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
U=/home/fabrice/git/pycsl-u56; cd $U || exit 2
export PYTHON_CPU_COUNT=4
SW=$U/scratchpad/u56/sw/base; C=$U/scratchpad/u56/census
mkdir -p $C
ls $SW/mir/*.mlw > $C/mir.list; ls $SW/bd/*.mlw > $C/bd.list; ls $SW/bd/pyref/*.mlw > $C/pyref.list
wc -l $C/*.list
for t in head base; do
  T=$U; [ $t = base ] && T=/home/fabrice/git/pycsl-u56-base
  for s in mir bd pyref; do
    echo "== $t $s $(date -u)"; echo "$(date -u) job2 census $t $s" >> $U/progress.txt
    PYTHONHASHSEED=0 timeout 7200 .venv/bin/python3 -W ignore scratchpad/u56/census.py $T $C/$t-$s.tsv $C/$s.list 2>&1 | grep -v '^\[\*\]' | tail -40
  done
done
echo "$(date -u) job2 done" >> $U/progress.txt
