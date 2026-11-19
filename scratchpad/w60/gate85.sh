#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
S=/tmp/claude-1000/-home-fabrice-git-pycsl/72fe2917-7b27-4e52-98dc-bfc0f750b42c/scratchpad
P=getting-better/proofs49
echo "$(date -u +%H:%M) started w60 gate85: conformance + sweeps (routes #85/#86)" >> $P/queue49.progress
bash bin/run-conformance.sh > $P/w60_conformance_r85.log 2>&1; echo $? > $P/w60_conformance_r85.rc
bash bin/check-self-annotate-sync.sh > $P/w60_fidelity_r85.log 2>&1; echo $? > $P/w60_fidelity_r85.rc
bash $S/wt85/bin/byte-diff-sweep.sh $S/sw85_base > $P/w60_sweep85_base.log 2>&1
bash bin/byte-diff-sweep.sh $S/sw85_cand > $P/w60_sweep85_cand.log 2>&1
(cd $S/wt85 && bash bin/mirror-emit-sweep.sh $S/mir85_base > /dev/null 2>&1)
bash bin/mirror-emit-sweep.sh $S/mir85_cand > /dev/null 2>&1
echo "$(date -u +%H:%M) w60 gate85 sweeps done" >> $P/queue49.progress
touch $P/w60_gate85_sweeps.done
