#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
P=getting-better/proofs49
echo "$(date -u +%H:%M) started w60_planes_route85 (--slow)" >> $P/queue49.progress
bash bin/run-soundness-planes.sh --slow > $P/w60_planes_route85.log 2>&1
echo $? > $P/w60_planes_route85.rc
echo "$(date -u +%H:%M) finished w60_planes_route85 rc=$(cat $P/w60_planes_route85.rc)" >> $P/queue49.progress
echo "$(date -u +%H:%M) started suite60_run3 (routes #85/#86)" >> $P/queue49.progress
bash bin/run-reference-tests.sh > $P/suite60_run3.log 2>&1
echo $? > $P/suite60_run3.rc
echo "$(date -u +%H:%M) finished suite60_run3 rc=$(cat $P/suite60_run3.rc)" >> $P/queue49.progress
touch $P/w60_gate85b.done
