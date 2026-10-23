#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
P=getting-better/proofs49
echo "$(date -u +%H:%M) started w60 FINAL planes (after value-differential 36->45)" >> $P/queue49.progress
bash bin/run-soundness-planes.sh --slow > $P/w60_planes_final.log 2>&1
echo $? > $P/w60_planes_final.rc
echo "$(date -u +%H:%M) finished w60 FINAL planes rc=$(cat $P/w60_planes_final.rc)" >> $P/queue49.progress
