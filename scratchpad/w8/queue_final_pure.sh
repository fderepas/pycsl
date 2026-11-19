#!/bin/bash
# Route #20 moved pure_ast's emission, so the in-flight a_pure verdict is for the PREVIOUS
# emission. Re-prove pure_ast at HEAD once the owed battery finishes.
cd /home/fabrice/git/pycsl
P=scratchpad/w7/proofs
while [ ! -f $P/OWED_DONE ]; do sleep 120; done
./scratchpad/w7/pr2.sh src/self-annotate/src/frontend/pure_ast.py o_pure2 28800
echo "FINAL PURE_AST RE-PROOF COMPLETE rc=$(cat $P/o_pure2.rc)" > $P/FINAL_DONE
