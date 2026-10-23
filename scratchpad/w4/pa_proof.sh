#!/bin/bash
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
cd /home/fabrice/git/pycsl
PYTHONHASHSEED=0 timeout 7200 python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/pure_ast.py --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' > scratchpad/w4/proofs/pure_ast.log 2>&1
echo $? > scratchpad/w4/proofs/pure_ast.rc
