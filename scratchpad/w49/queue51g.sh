#!/bin/bash
# Queue G (relaunch #51) — the SEVEN mirror re-proofs ROUTE #57 owes.
# Measured with bin/mirror-emit-sweep.sh + byte-diff-compare.py at the post-#56 HEAD:
# route #57 moves exactly these seven emissions, 0 GONE and 0 APPEARED.
# ORDERED DURABLE-FIRST: the five quicker files run first so their verdicts bank early;
# expressions and statements (each ~3-4h, and each of which had NEVER completed before
# this window) run LAST, as a pair, at concurrency TWO.
cd /home/fabrice/git/pycsl
Q=(
  "module6_whyml/auto_trust.py:w51g_autotrust"
  "module6_whyml/types.py:w51g_types"
  "module6_whyml/functions.py:w51g_functions"
  "module6_whyml/preamble.py:w51g_preamble"
  "module6_whyml/stmt_control_flow.py:w51g_scf"
  "module6_whyml/expressions.py:w51g_expressions"
  "module6_whyml/statements.py:w51g_statements"
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
echo "$(date -u +%H:%M) QUEUE G DONE" >> getting-better/proofs49/queue49.progress
touch getting-better/proofs49/QUEUE51G_DONE
