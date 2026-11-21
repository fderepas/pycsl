#!/bin/bash
# gates2.sh : census rows + remeasure + planes + checks for g4. Run AS ONE heavy.sh job.
G=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/g4
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
W=/home/fabrice/git/pycsl-g4
L=$G/gates; mkdir -p $L
cd $W
.venv/bin/python3 getting-better/systematic-soundness-r3/g4-r432-437/census.py $W > $L/census.log 2>&1; echo "census rc=$?" >> $L/rc.txt
.venv/bin/python3 $G/remeasure.py $W 4621_gen37_r343_self_max_noexc.py 4810_gen37_r358_join_self_noexc.py >> $L/census.log 2>&1; echo "remeasure rc=$?" >> $L/rc.txt
bash bin/run-soundness-planes.sh > $L/planes.log 2>&1; echo "planes rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-refusal-witness-coverage.py > $L/rwc.log 2>&1; echo "rwc rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-refusal-advice-audited.py > $L/advice.log 2>&1; echo "advice rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-getattr-erasure.py > $L/getattr.log 2>&1; echo "getattr rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-clause-survival.py --emit-dir $G/ca2 > $L/clause.log 2>&1; echo "clause rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-assumed-facts.py --emit-dir $G/ca2 > $L/assumed.log 2>&1; echo "assumed rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-open-route-carriers.py > $L/carriers.log 2>&1; echo "carriers rc=$?" >> $L/rc.txt
python3 bin/doc-coherency.py --check > $L/doc.log 2>&1; echo "doc rc=$?" >> $L/rc.txt
$G/scr.sh /home/fabrice/git/pycsl-g4-base $G/m1base --full 2 /home/fabrice/git/pycsl-g4-base/test-suite/corpus/pycsl-reference/4810_gen37_r358_join_self_noexc.py /home/fabrice/git/pycsl-g4-base/test-suite/corpus/pycsl-reference/4621_gen37_r343_self_max_noexc.py > $L/m1.log 2>&1
$G/scr.sh /home/fabrice/git/pycsl-g4 $G/m1cand --full 2 /home/fabrice/git/pycsl-g4/test-suite/corpus/pycsl-reference/4810_gen37_r358_join_self_noexc.py /home/fabrice/git/pycsl-g4/test-suite/corpus/pycsl-reference/4621_gen37_r343_self_max_noexc.py >> $L/m1.log 2>&1
echo GATESDONE >> $L/rc.txt
