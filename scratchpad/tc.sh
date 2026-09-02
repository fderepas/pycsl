#!/bin/bash
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
cd /home/fabrice/git/pycsl
S=/tmp/claude-1000/-home-fabrice-git-pycsl/8f7f6044-5a3d-4979-a728-07c3eb57e115/scratchpad
timeout 900 env PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/pure_ast.py --import-path src/pycsl --no-proof --keep-mlw >$S/tc.log 2>&1
rc=$?
if [ $rc -eq 0 ]; then echo "L3-tc GREEN"; else grep -v "^Warning" $S/tc.log | tail -8; fi
