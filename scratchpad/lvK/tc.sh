#!/bin/bash
# tc.sh <tree> <tag> <rel>... : --no-proof --keep-mlw (QUICK)
T=$1; tag=$2; shift 2; O=/home/fabrice/git/pycsl-lvK/scratchpad/lvK/tc
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
cd $T
for rel in "$@"; do f=src/self-annotate/src/$rel; m=${f%.py}.mlw; k=$(echo ${rel%.py} | tr / _)
  rm -f $m; timeout 1500 python3 src/pycsl/pycsl.py $f --import-path $T/src/pycsl --no-proof --keep-mlw > $O/$tag.$k.log 2>&1; echo "rc=$?" >> $O/$tag.$k.log
  [ -f $m ] && mv $m $O/$tag.$k.mlw
done
