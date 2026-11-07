#!/bin/bash
# Route #44/#45 mirror re-proof queue: 5 files, THREE concurrent, longest first.
cd /home/fabrice/git/pycsl
Q=(
  "frontend/pure_ast.py:r45_pureast"
  "module6_whyml/stmt_control_flow.py:r45_scf"
  "module6_whyml/expressions.py:r45_expressions"
  "frontend/desugar.py:r45_desugar"
  "proof2why3/sertop.py:r45_sertop"
)
for item in "${Q[@]}"; do
  f="src/self-annotate/src/${item%%:*}"
  n="${item##*:}"
  while [ "$(jobs -rp | wc -l)" -ge 3 ]; do sleep 20; done
  bash scratchpad/w48/pr.sh "$f" "$n" 28800 &
  echo "$(date -u +%H:%M) started $n" >> getting-better/proofs48/queue48.progress
done
wait
echo "$(date -u +%H:%M) QUEUE DONE" >> getting-better/proofs48/queue48.progress
touch getting-better/proofs48/QUEUE48_DONE
