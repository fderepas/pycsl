#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u75/scratchpad/u75/tmp; mkdir -p "$TMPDIR"
# chain2.sh : (one job) probe + witness battery (q then full proof of q-SUCCESS) on h2, h2 sweep + compare vs b1,
# then the same battery on b2 (L21 main) and b1 (u73 e1b967928 src)
U=/home/fabrice/git/pycsl-u75/scratchpad/u75
echo "chain2 start $(date -u)"
bash $U/tools/PB.sh /home/fabrice/git/pycsl-u75-h2 h2 > $U/logs/PB-h2.txt 2>&1; echo "PB h2 done $(date -u) $(grep -c '' $U/logs/PB-h2.txt)"
bash $U/tools/S.sh /home/fabrice/git/pycsl-u75-h2 $U/logs/G/h2
bash $U/tools/CMP.sh h2 b1
bash $U/tools/PB.sh /home/fabrice/git/pycsl-u75-b2 b2 > $U/logs/PB-b2.txt 2>&1; echo "PB b2 done $(date -u)"
bash $U/tools/PB.sh /home/fabrice/git/pycsl-u75-b1 b1 > $U/logs/PB-b1.txt 2>&1; echo "PB b1 done $(date -u)"
echo "chain2 end $(date -u)"
