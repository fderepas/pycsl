#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/w48/tmp
f="$1"; n="$2"; t="${3:-28800}"
PYTHONHASHSEED=0 timeout "$t" python3 -u src/pycsl/pycsl.py "$f" --import-path src/pycsl --provers "Alt-Ergo,2.6.3,,Z3,4.13.3," > getting-better/proofs48/$n.log 2>&1
echo $? > getting-better/proofs48/$n.rc
