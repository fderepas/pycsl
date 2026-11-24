#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u75/scratchpad/u75/tmp; mkdir -p "$TMPDIR"
# chain1.sh : (one job) h1 --no-proof probe check (u75 + rt83 + witnesses), then the h1 MEASURE sweep and its compare vs b1
U=/home/fabrice/git/pycsl-u75/scratchpad/u75; H=/home/fabrice/git/pycsl-u75-h1
echo "chain1 start $(date -u)"
bash $U/tools/Q.sh $H h1q u75 rt83 | sed 's/^/[Q] /'
bash $U/tools/wit.sh q $H $U/logs/W-h1q | sed 's/^/[W] /'
bash $U/tools/S.sh $H $U/logs/G/h1
bash $U/tools/CMP.sh h1 b1
echo "chain1 end $(date -u)"
