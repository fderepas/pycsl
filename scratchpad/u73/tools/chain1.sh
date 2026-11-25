#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u73/scratchpad/u73/tmp; mkdir -p "$TMPDIR"
# chain1.sh : (one NORMAL job, after the base sweep) sweep h1 + compare vs base; probe battery on bh, b0, h1.
U=/home/fabrice/git/pycsl-u73/scratchpad/u73
echo "chain1 start $(date -u)"
bash $U/tools/S.sh /home/fabrice/git/pycsl-u73-h1 $U/logs/G/h1
bash $U/tools/CMP.sh h1
for t in h1:/home/fabrice/git/pycsl-u73-h1 bh:/home/fabrice/git/pycsl-u73-bh b0:/home/fabrice/git/pycsl-u73-b0; do
  bash $U/tools/J.sh ${t#*:} ${t%%:*} 2>&1 | sed "s/^/[J ${t%%:*}] /"; done
echo "chain1 end $(date -u)"
