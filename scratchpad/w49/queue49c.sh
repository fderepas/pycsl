#!/bin/bash
# Queue C — the SIX mirrors whose emission moves under routes #46/#50 (measured: 109 lines
# over six files; pure_ast and sertop do NOT move and keep their standing verdicts).
# Waits for queue B's `functions` proof to finish so the machine never runs more than TWO
# whole-file proofs at once (#48's measured over-subscription lesson).
cd /home/fabrice/git/pycsl
while [ ! -f getting-better/proofs49/w49_functions.rc ]; do sleep 60; done
Q=(
  "module6_whyml/expressions.py:w49b_expressions"
  "module6_whyml/statements.py:w49b_statements"
  "frontend/Module5_IREmitter.py:w49b_m5ir"
  "module6_whyml/stmt_control_flow.py:w49b_scf"
  "module6_whyml/types.py:w49b_types"
  "frontend/Module2_Parser.py:w49b_m2p"
)
for item in "${Q[@]}"; do
  f="src/self-annotate/src/${item%%:*}"
  n="${item##*:}"
  while [ "$(jobs -rp | wc -l)" -ge 2 ]; do sleep 20; done
  bash scratchpad/w49/pr.sh "$f" "$n" 28800 &
  echo "$(date -u +%H:%M) started $n" >> getting-better/proofs49/queue49.progress
done
wait
echo "$(date -u +%H:%M) QUEUE C DONE" >> getting-better/proofs49/queue49.progress
touch getting-better/proofs49/QUEUE49C_DONE
