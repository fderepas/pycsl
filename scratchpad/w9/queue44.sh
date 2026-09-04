#!/bin/bash
# Drains the four proofs owed by routes #23/#24, TWO AT A TIME, after the two
# in flight (r22_scf, r23_m5) finish. Writes only under scratchpad/w7/proofs.
cd /home/fabrice/git/pycsl
P=scratchpad/w7/proofs
while [ ! -f $P/r22_scf.rc ] || [ ! -f $P/r23_m5.rc ]; do sleep 120; done
./scratchpad/w7/pr2.sh src/self-annotate/src/frontend/pure_ast.py r24_pure 28800 &
./scratchpad/w7/pr2.sh src/self-annotate/src/frontend/ir_resolve.py r23_irr 28800 &
wait
echo "PAIR1 DONE pure=$(cat $P/r24_pure.rc) irr=$(cat $P/r23_irr.rc)" > $P/Q44_PAIR1
./scratchpad/w7/pr2.sh src/self-annotate/src/frontend/__init__.py r23_finit 28800 &
./scratchpad/w7/pr2.sh src/self-annotate/src/pycsl.py r23_pycsl 28800 &
wait
echo "PAIR2 DONE finit=$(cat $P/r23_finit.rc) pycsl=$(cat $P/r23_pycsl.rc)" > $P/Q44_PAIR2
echo "ALL FOUR DONE" > $P/Q44_DONE
