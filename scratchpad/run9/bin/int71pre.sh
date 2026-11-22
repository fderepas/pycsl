#!/bin/bash
# int71 (L16b = L15 + batch A): mirror sweep, proof-map compare vs lvW SRC-FINAL emission, pycsl whole-file, then battery ACDEF
O=/home/fabrice/git/pycsl/scratchpad/run9/int71; mkdir -p $O; H=/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
cd /home/fabrice/git/pycsl-int71 || exit 1
HEAVY_PRIO=1 $H bin/mirror-emit-sweep.sh $O/mir > $O/mir.log 2>&1; echo "mir rc=$?" > $O/pre.txt
diff -rq /home/fabrice/git/pycsl/scratchpad/run9/v66/mir-int $O/mir >> $O/pre.txt 2>&1
for f in module6_whyml__statements.mlw module6_whyml__stmt_control_flow.mlw pycsl.mlw; do cmp -s /home/fabrice/git/pycsl/scratchpad/run9/evidence/lvW/mir-b65/$f $O/mir/$f && echo "$f identical-to-b65" || echo "$f DIFFERS-from-b65"; done >> $O/pre.txt
PQ_ENV="HEAVY_PRIO=1 PYTHON_CPU_COUNT=4" bash /home/fabrice/git/pycsl/scratchpad/run9/bin/proveq.sh /home/fabrice/git/pycsl-int71 int71 pycsl.py
echo PROOF-DONE >> $O/pre.txt
cd /home/fabrice/git/pycsl && STEPS=ACDEF HEAVY_PRIO=1 PYTHON_CPU_COUNT=6 BASE_BD=/home/fabrice/git/pycsl/scratchpad/run9/v66/bd-int BASE_MIR=/home/fabrice/git/pycsl/scratchpad/run9/v66/mir-int bash scratchpad/run9/bin/battery.sh v70 /home/fabrice/git/pycsl-int71 /home/fabrice/git/pycsl
echo DONE >> $O/pre.txt
