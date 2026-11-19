#!/bin/bash
# mutemit.sh <rel> <subs> <tag> : mutate the st copy, --no-proof --keep-mlw, save the mlw, restore (QUICK)
L=/home/fabrice/git/pycsl-lvD/scratchpad/lvD; T=$L/st; cd $T; export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0
f=src/self-annotate/src/$1; cp $f /tmp/lvdmut.$$; SUBS=$L/$2 python3 $L/sub.py $f > $L/fun/$3.patchlog 2>&1
timeout 900 python3 src/pycsl/pycsl.py $f --import-path src/pycsl --no-proof --keep-mlw > $L/fun/$3.log 2>&1; echo "rc=$?" >> $L/fun/$3.log
mv ${f%.py}.mlw $L/$3.mlw; cp /tmp/lvdmut.$$ $f; rm -f /tmp/lvdmut.$$
