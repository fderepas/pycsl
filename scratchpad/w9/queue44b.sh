#!/bin/bash
# Drains the five proofs owed by routes #23/#24/#28, TWO AT A TIME.
# Writes only under scratchpad/w7/proofs and TMPDIR — never the repo tree.
cd /home/fabrice/git/pycsl
P=scratchpad/w7/proofs
./scratchpad/w7/pr2.sh src/self-annotate/src/frontend/Module5_IREmitter.py f_m5 28800
echo "M5 DONE rc=$(cat $P/f_m5.rc)" > $P/F_M5
./scratchpad/w7/pr2.sh src/self-annotate/src/frontend/ir_resolve.py f_irr 28800 &
./scratchpad/w7/pr2.sh src/self-annotate/src/frontend/__init__.py f_finit 28800 &
wait
echo "PAIR1 rc irr=$(cat $P/f_irr.rc) finit=$(cat $P/f_finit.rc)" > $P/F_PAIR1
./scratchpad/w7/pr2.sh src/self-annotate/src/pycsl.py f_pycsl 28800 &
./scratchpad/w7/pr2.sh src/self-annotate/src/frontend/pure_ast.py f_pure 28800 &
wait
echo "PAIR2 rc pycsl=$(cat $P/f_pycsl.rc) pure=$(cat $P/f_pure.rc)" > $P/F_PAIR2
echo ALL DONE > $P/F_DONE
