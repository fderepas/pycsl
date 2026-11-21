#!/bin/bash
# Queue D — relaunch of the killed queue C. The SIX mirrors whose emission moves under
# routes #46/#50. REORDERED DURABLE-FIRST: the four that queue C never reached run first
# at concurrency TWO, so their verdicts bank early; expressions and statements (the two
# that each need >55min) run LAST, as a pair, alone on the machine.
cd /home/fabrice/git/pycsl
Q=(
  "frontend/Module5_IREmitter.py:w49d_m5ir"
  "module6_whyml/stmt_control_flow.py:w49d_scf"
  "module6_whyml/types.py:w49d_types"
  "frontend/Module2_Parser.py:w49d_m2p"
  "module6_whyml/expressions.py:w49d_expressions"
  "module6_whyml/statements.py:w49d_statements"
)
for item in "${Q[@]}"; do
  f="src/self-annotate/src/${item%%:*}"
  n="${item##*:}"
  while [ "$(jobs -rp | wc -l)" -ge 2 ]; do sleep 20; done
  bash scratchpad/w49/pr.sh "$f" "$n" 28800 &
  echo "$(date -u +%H:%M) started $n" >> getting-better/proofs49/queue49.progress
  sleep 5
done
wait
echo "$(date -u +%H:%M) QUEUE D DONE" >> getting-better/proofs49/queue49.progress
touch getting-better/proofs49/QUEUE49D_DONE
