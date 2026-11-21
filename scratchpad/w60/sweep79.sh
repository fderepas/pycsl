#!/bin/bash
S=/tmp/claude-1000/-home-fabrice-git-pycsl/72fe2917-7b27-4e52-98dc-bfc0f750b42c/scratchpad
P=/home/fabrice/git/pycsl/getting-better/proofs49
cd /home/fabrice/git/pycsl
echo "$(date -u +%H:%M) started w60 byte-diff sweeps (route #79)" >> $P/queue49.progress
bash $S/wt79/bin/byte-diff-sweep.sh $S/sw79_base > $P/w60_sweep_base.log 2>&1
echo "$(date -u +%H:%M) base sweep done rc=$?" >> $P/queue49.progress
bash bin/byte-diff-sweep.sh $S/sw79_cand > $P/w60_sweep_cand.log 2>&1
echo "$(date -u +%H:%M) cand sweep done rc=$?" >> $P/queue49.progress
touch $P/w60_sweeps.done
