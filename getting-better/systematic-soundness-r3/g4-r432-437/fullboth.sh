#!/bin/bash
# fullboth.sh : full-proof verdicts of the g4 witnesses / controls / advice probes at base and candidate,
# then the gate battery. Run AS ONE heavy.sh job (sequential inside).
G=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/g4
$G/scr.sh /home/fabrice/git/pycsl-g4-base $G/fbase --full 4 $(cat $G/full-base.txt)
$G/scr.sh /home/fabrice/git/pycsl-g4 $G/fcand --full 4 $(cat $G/full-cand.txt)
echo ALLDONE
# ---- gate battery (sequential, one job) ----
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
W=/home/fabrice/git/pycsl-g4; B=/home/fabrice/git/pycsl-g4-base; V=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/v8
L=$G/gates; mkdir -p $L
cd $W
bash bin/check-self-annotate-sync.sh > $L/sync.log 2>&1; echo "sync rc=$?" >> $L/rc.txt
bash bin/self-annotate-mirror-check.sh > $L/mcheck.log 2>&1; echo "mcheck rc=$?" >> $L/rc.txt
bash bin/mirror-emit-sweep.sh $G/ma > $L/ma.log 2>&1; echo "ma rc=$?" >> $L/rc.txt
if grep -q DONE-C $V/outC.txt 2>/dev/null && [ -d $V/mb ]; then echo "mb from driver v8" >> $L/rc.txt; MB=$V/mb; else
  cd $B && bash bin/mirror-emit-sweep.sh $G/mb > $L/mb.log 2>&1; echo "mb rc=$?" >> $L/rc.txt; MB=$G/mb; cd $W; fi
python3 bin/byte-diff-compare.py $MB $G/ma --min-files 45 > $L/cmp-mirror.log 2>&1; echo "cmp-mirror rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-refusal-witness-coverage.py --append-new > $L/census.log 2>&1; echo "append-new rc=$?" >> $L/rc.txt
.venv/bin/python3 $G/remeasure.py $W 4621_gen37_r343_self_max_noexc.py 4810_gen37_r358_join_self_noexc.py >> $L/census.log 2>&1; echo "remeasure rc=$?" >> $L/rc.txt
bash bin/run-soundness-planes.sh > $L/planes.log 2>&1; echo "planes rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-refusal-witness-coverage.py > $L/rwc.log 2>&1; echo "rwc rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-refusal-advice-audited.py > $L/advice.log 2>&1; echo "advice rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-getattr-erasure.py > $L/getattr.log 2>&1; echo "getattr rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-clause-survival.py --emit-dir $G/ca2 > $L/clause.log 2>&1; echo "clause rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-assumed-facts.py --emit-dir $G/ca2 > $L/assumed.log 2>&1; echo "assumed rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-open-route-carriers.py > $L/carriers.log 2>&1; echo "carriers rc=$?" >> $L/rc.txt
python3 bin/doc-coherency.py --check > $L/doc.log 2>&1; echo "doc rc=$?" >> $L/rc.txt
echo GATESDONE >> $L/rc.txt
