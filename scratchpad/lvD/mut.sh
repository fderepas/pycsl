#!/bin/bash
# mut.sh <rel> <funname> <subs> <tag> [--no-proof] : mutate the st copy, prove --fun (or emit), restore. via heavy.sh
L=/home/fabrice/git/pycsl-lvD/scratchpad/lvD; T=$L/st; cd $T; export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
f=src/self-annotate/src/$1; cp $f /tmp/lvdmut.$$; SUBS=$L/$3 python3 $L/sub.py $f > $L/fun/$4.patchlog 2>&1
timeout 3000 python3 src/pycsl/pycsl.py $f --import-path src/pycsl --fun "$2" $5 > $L/fun/$4.log 2>&1; echo "rc=$?" >> $L/fun/$4.log
cp /tmp/lvdmut.$$ $f; rm -f /tmp/lvdmut.$$ ${f%.py}.mlw
