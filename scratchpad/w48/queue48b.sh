#!/bin/bash
# FINAL-STATE mirror re-proof queue: the six mirrors whose emission moved for routes
# #47/#48/#49. TWO concurrent, longest first — the #48 lesson: each pycsl run's VACUITY
# pass spawns about six parallel `why3 prove` calls, so three concurrent proofs put
# eighteen why3 processes on twelve cores and individual 5-second goals took nine minutes.
cd /home/fabrice/git/pycsl
Q=(
  "module6_whyml/expressions.py:f48_expressions"
  "module6_whyml/stmt_control_flow.py:f48_scf"
  "module6_whyml/statements.py:f48_statements"
  "module6_whyml/functions.py:f48_functions"
  "frontend/exec_splice.py:f48_exec_splice"
  "frontend/desugar.py:f48_desugar"
)
for item in "${Q[@]}"; do
  f="src/self-annotate/src/${item%%:*}"
  n="${item##*:}"
  while [ "$(jobs -rp | wc -l)" -ge 2 ]; do sleep 20; done
  bash scratchpad/w48/pr.sh "$f" "$n" 28800 &
  echo "$(date -u +%H:%M) started $n" >> getting-better/proofs48/queue48b.progress
done
wait
echo "$(date -u +%H:%M) QUEUE48B DONE" >> getting-better/proofs48/queue48b.progress
touch getting-better/proofs48/QUEUE48B_DONE
