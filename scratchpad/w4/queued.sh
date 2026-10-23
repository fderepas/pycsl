#!/bin/bash
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
cd /home/fabrice/git/pycsl
until [ -f scratchpad/w4/proofs/pure_ast.rc ]; do sleep 30; done
exec scratchpad/w4/runproofs.sh module6_whyml/statements.py module6_whyml/stmt_control_flow.py module6_whyml/expressions.py
