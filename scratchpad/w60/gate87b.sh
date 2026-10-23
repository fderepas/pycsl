#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
S=/tmp/claude-1000/-home-fabrice-git-pycsl/72fe2917-7b27-4e52-98dc-bfc0f750b42c/scratchpad
P=getting-better/proofs49
echo "$(date -u +%H:%M) started w60 gate87b: sweeps + planes + suite (route #87)" >> $P/queue49.progress
bash $S/wt87/bin/byte-diff-sweep.sh $S/sw87_base > $P/w60_sweep87_base.log 2>&1
bash bin/byte-diff-sweep.sh $S/sw87_cand > $P/w60_sweep87_cand.log 2>&1
(cd $S/wt87 && bash bin/mirror-emit-sweep.sh $S/mir87_base > /dev/null 2>&1)
bash bin/mirror-emit-sweep.sh $S/mir87_cand > /dev/null 2>&1
echo "$(date -u +%H:%M) gate87b sweeps done" >> $P/queue49.progress
touch $P/w60_gate87_sweeps.done
bash bin/run-soundness-planes.sh --slow > $P/w60_planes_route87.log 2>&1
echo $? > $P/w60_planes_route87.rc
echo "$(date -u +%H:%M) finished w60_planes_route87 rc=$(cat $P/w60_planes_route87.rc)" >> $P/queue49.progress
bash bin/run-reference-tests.sh > $P/suite60_run4.log 2>&1
echo $? > $P/suite60_run4.rc
echo "$(date -u +%H:%M) finished suite60_run4 rc=$(cat $P/suite60_run4.rc)" >> $P/queue49.progress
touch $P/w60_gate87b.done
