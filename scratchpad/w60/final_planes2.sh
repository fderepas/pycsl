#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
P=getting-better/proofs49
echo "$(date -u +%H:%M) started w60 FINAL planes #2 (after no-exception-differential 39->43)" >> $P/queue49.progress
bash bin/run-soundness-planes.sh --slow > $P/w60_planes_final2.log 2>&1
echo $? > $P/w60_planes_final2.rc
echo "$(date -u +%H:%M) finished w60 FINAL planes #2 rc=$(cat $P/w60_planes_final2.rc)" >> $P/queue49.progress
