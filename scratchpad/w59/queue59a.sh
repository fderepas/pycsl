#!/bin/bash
# Queue A (gen #9) — the ONE mirror re-proof route #80 owes.
# #80 edits `_py_stmt_delete` in src/self-annotate/src/frontend/Module5_IREmitter.py
# (an UN-trusted verified body port with a bespoke Module6 lowering), so the whole-file
# Module5 mirror proof must be re-run. #77's equivalent (w58_m5ir) took 52 min, rc=0,
# 2108 goals Valid.
cd /home/fabrice/git/pycsl
bash scratchpad/w49/pr.sh src/self-annotate/src/frontend/Module5_IREmitter.py w59a_m5ir 28800
echo "$(date -u +%H:%M) QUEUE 59A DONE" >> getting-better/proofs49/queue49.progress
touch getting-better/proofs49/QUEUE59A_DONE
