#!/bin/bash
# int68 pre-gates: mirror sweep, proof-map compare vs snapA (lvW's sweep at SRC-FINAL), then pycsl.py whole-file
O=/home/fabrice/git/pycsl/scratchpad/run9/int68; mkdir -p $O; H=/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
cd /home/fabrice/git/pycsl-int68 || exit 1
HEAVY_PRIO=1 $H bin/mirror-emit-sweep.sh $O/mir > $O/mir.log 2>&1; echo "mir rc=$?" > $O/pre.txt
diff -rq /home/fabrice/git/pycsl/scratchpad/run9/base8/mir $O/mir > $O/D-vs-base8.txt 2>&1
for f in module6_whyml__statements.mlw module6_whyml__stmt_control_flow.mlw pycsl.mlw; do cmp -s /home/fabrice/git/pycsl/scratchpad/run9/evidence/lvW/mir-b65/$f $O/mir/$f && echo "$f identical-to-b65" || echo "$f DIFFERS-from-b65"; done >> $O/pre.txt
cd /home/fabrice/git/pycsl-int68 && bash /home/fabrice/git/pycsl/scratchpad/run9/bin/proveq.sh /home/fabrice/git/pycsl-int68 int68 pycsl.py
echo DONE >> $O/pre.txt
