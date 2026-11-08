#!/bin/bash
# Six owed whole-file mirror re-proofs at the FINAL tree state (routes #47/#48/#49 landed).
# CONCURRENCY TWO — measured lesson from #48: each pycsl run's vacuity pass spawns ~6
# parallel why3 calls, so three concurrent proofs over-subscribe 12 cores.
cd /home/fabrice/git/pycsl
Q=(
  "module6_whyml/statements.py:w49_statements"
  "module6_whyml/expressions.py:w49_expressions"
  "module6_whyml/functions.py:w49_functions"
  "module6_whyml/stmt_control_flow.py:w49_scf"
  "frontend/exec_splice.py:w49_exec_splice"
  "frontend/desugar.py:w49_desugar"
)
for item in "${Q[@]}"; do
  f="src/self-annotate/src/${item%%:*}"
  n="${item##*:}"
  while [ "$(jobs -rp | wc -l)" -ge 2 ]; do sleep 20; done
  bash scratchpad/w49/pr.sh "$f" "$n" 28800 &
  echo "$(date -u +%H:%M) started $n" >> getting-better/proofs49/queue49.progress
done
wait
echo "$(date -u +%H:%M) QUEUE DONE" >> getting-better/proofs49/queue49.progress
touch getting-better/proofs49/QUEUE49_DONE
