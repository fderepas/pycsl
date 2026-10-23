#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
P=getting-better/proofs49
echo "$(date -u +%H:%M) started w60_planes (route #83 gate, --slow)" >> $P/queue49.progress
bash bin/run-soundness-planes.sh --slow > $P/w60_planes_route83.log 2>&1
echo $? > $P/w60_planes_route83.rc
echo "$(date -u +%H:%M) finished w60_planes rc=$(cat $P/w60_planes_route83.rc)" >> $P/queue49.progress
echo "$(date -u +%H:%M) started suite60_run1 (route #83 gate)" >> $P/queue49.progress
bash bin/run-reference-tests.sh > $P/suite60_run1.log 2>&1
echo $? > $P/suite60_run1.rc
echo "$(date -u +%H:%M) finished suite60_run1 rc=$(cat $P/suite60_run1.rc)" >> $P/queue49.progress
