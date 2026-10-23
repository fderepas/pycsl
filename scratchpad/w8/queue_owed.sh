#!/bin/bash
# Wait for the two array-battery proofs, then run the six OWED re-proofs two at a time.
# Writes ONLY to scratchpad/w7/proofs and TMPDIR — it never mutates the repo tree.
cd /home/fabrice/git/pycsl
P=scratchpad/w7/proofs
while [ ! -f $P/a_expr.rc ] || [ ! -f $P/a_pure.rc ]; do sleep 60; done
run() { ./scratchpad/w7/pr2.sh "$1" "$2" 28800; }
# ordered cheapest-first so a verdict lands early
run src/self-annotate/src/frontend/desugar.py            o_desugar &
run src/self-annotate/src/audit_proof.py                 o_ap &
wait
run src/self-annotate/src/frontend/Module3_Weaver.py     o_m3w &
run src/self-annotate/src/frontend/ir_resolve.py         o_irr &
wait
run src/self-annotate/src/frontend/__init__.py           o_finit &
run src/self-annotate/src/Module6_WhyMLTranspiler.py     o_m6t &
wait
run src/self-annotate/src/module6_whyml/statements.py    o_stmts &
wait
echo "OWED BATTERY COMPLETE" > $P/OWED_DONE
