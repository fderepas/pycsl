#!/bin/bash
# fun.sh <tree> <rel> <funname> <tag> (NORMAL)
T=$1; rel=$2; fn=$3; tag=$4; O=/home/fabrice/git/pycsl-lvK/scratchpad/lvK/fun
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
cd $T; f=src/self-annotate/src/$rel
t0=$(date +%s)
timeout 9000 python3 src/pycsl/pycsl.py $f --import-path $T/src/pycsl --fun "$fn" > $O/$tag.log 2>&1; echo "rc=$? secs=$(( $(date +%s)-t0 ))" >> $O/$tag.log
rm -f ${f%.py}.mlw
