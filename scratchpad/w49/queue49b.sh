#!/bin/bash
# Re-ordered queue: DURABLE FIRST. The combined route #46/#50 build (measured in the
# spike) moves the emission of SEVEN mirrors — Module2_Parser, Module5_IREmitter,
# pure_ast, expressions, statements, stmt_control_flow, types — so proofs of those files
# are superseded the moment it lands. functions, exec_splice and desugar do NOT move under
# it, so their verdicts hold in BOTH worlds and they go first. CONCURRENCY TWO (#48's
# measured lesson: each run's vacuity pass spawns ~6 parallel why3 calls).
cd /home/fabrice/git/pycsl
Q=(
  "module6_whyml/functions.py:w49_functions"
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
echo "$(date -u +%H:%M) QUEUE B DONE" >> getting-better/proofs49/queue49.progress
touch getting-better/proofs49/QUEUE49B_DONE
