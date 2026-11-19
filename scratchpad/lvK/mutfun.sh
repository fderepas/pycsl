#!/bin/bash
# mutfun.sh <rel> <funname> <tag> : --fun on the stm mutated copy (NORMAL)
L=/home/fabrice/git/pycsl-lvK/scratchpad/lvK; T=$L/stm; cd $T; export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
f=src/self-annotate/src/$1
timeout 9000 python3 src/pycsl/pycsl.py $f --import-path $T/src/pycsl --fun "$2" > $L/fun/$3.log 2>&1; echo "rc=$?" >> $L/fun/$3.log
rm -f ${f%.py}.mlw
