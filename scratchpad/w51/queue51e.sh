#!/bin/bash
# Queue E — the re-proofs route #51 OWES: the two mirrors it moves that queue D does not
# already re-run on the landed tree. `frontend/Module2_Parser` is NOT here because queue D
# reaches it AFTER route #51 landed, so queue D proves the landed file.
#   w51_scf  — stmt_control_flow, 75 lines, a VERIFIED (not \trusted) method and its caller
#              change shape and a previously-DELETED branch becomes reachable. The one to
#              watch. Queue D's own w49d_scf verdict is for the SUPERSEDED file and is kept
#              deliberately as the before/after baseline.
#   w51_cis  — core_ir_semantic, 98 lines, the two new Module 4 functions mirrored as
#              VERIFIED bodies (not \trusted stubs), which is what keeps the metric flat.
cd /home/fabrice/git/pycsl
while [ ! -f getting-better/proofs49/QUEUE49D_DONE ]; do sleep 60; done
Q=(
  "module6_whyml/stmt_control_flow.py:w51_scf"
  "core_ir_semantic.py:w51_cis"
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
echo "$(date -u +%H:%M) QUEUE E DONE" >> getting-better/proofs49/queue49.progress
touch getting-better/proofs49/QUEUE51E_DONE
