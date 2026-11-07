#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/w7/tmp
f="$1"; n="$2"
PYTHONHASHSEED=0 timeout 10800 python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl --provers "Alt-Ergo,2.6.3,,Z3,4.13.3," > scratchpad/w7/proofs/$n.log 2>&1
echo $? > scratchpad/w7/proofs/$n.rc
