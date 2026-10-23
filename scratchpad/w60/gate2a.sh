#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
S=/tmp/claude-1000/-home-fabrice-git-pycsl/72fe2917-7b27-4e52-98dc-bfc0f750b42c/scratchpad
P=getting-better/proofs49
echo "$(date -u +%H:%M) started w60 gate2a (Gap 2a: conformance + fidelity + sweeps + planes + suite)" >> $P/queue49.progress
bash bin/run-conformance.sh > $P/w60_conformance_2a.log 2>&1; echo $? > $P/w60_conformance_2a.rc
bash bin/check-self-annotate-sync.sh > $P/w60_fidelity_2a.log 2>&1; echo $? > $P/w60_fidelity_2a.rc
bash $S/wt2a/bin/byte-diff-sweep.sh $S/sw2a_base > $P/w60_sweep2a_base.log 2>&1
bash bin/byte-diff-sweep.sh $S/sw2a_cand > $P/w60_sweep2a_cand.log 2>&1
(cd $S/wt2a && bash bin/mirror-emit-sweep.sh $S/mir2a_base > /dev/null 2>&1)
bash bin/mirror-emit-sweep.sh $S/mir2a_cand > /dev/null 2>&1
echo "$(date -u +%H:%M) gate2a sweeps done (conformance rc=$(cat $P/w60_conformance_2a.rc))" >> $P/queue49.progress
touch $P/w60_gate2a_sweeps.done
bash bin/run-soundness-planes.sh --slow > $P/w60_planes_2a.log 2>&1
echo $? > $P/w60_planes_2a.rc
echo "$(date -u +%H:%M) finished w60_planes_2a rc=$(cat $P/w60_planes_2a.rc)" >> $P/queue49.progress
bash bin/run-reference-tests.sh > $P/suite60_run5.log 2>&1
echo $? > $P/suite60_run5.rc
echo "$(date -u +%H:%M) finished suite60_run5 rc=$(cat $P/suite60_run5.rc)" >> $P/queue49.progress
touch $P/w60_gate2a.done
