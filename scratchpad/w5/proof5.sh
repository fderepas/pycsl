#!/bin/bash
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/tmp
mkdir -p "$TMPDIR"
cd /home/fabrice/git/pycsl
PYTHONHASHSEED=0 timeout 14400 python3 src/pycsl/pycsl.py src/self-annotate/src/frontend/pure_ast.py --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' > scratchpad/w5/proofs/pure_ast_2.log 2>&1
echo $? > scratchpad/w5/proofs/pure_ast_2.rc
