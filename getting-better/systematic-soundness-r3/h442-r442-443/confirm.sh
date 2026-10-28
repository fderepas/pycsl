#!/bin/bash
# h442 final-candidate confirmation after the DVW nested-def tightening. Run AS ONE heavy.sh job.
H=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/h442
V=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/v10
W=/home/fabrice/git/pycsl-h442
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
L=$H/gates-final; mkdir -p $L; : > $L/rc.txt
cd $W
echo "start $(date -u +%FT%TZ) $(md5sum src/pycsl/pycsl.py | cut -c1-12)" >> $L/rc.txt
bash bin/check-self-annotate-sync.sh > $L/sync.log 2>&1; echo "sync rc=$?" >> $L/rc.txt
bash bin/self-annotate-mirror-check.sh > $L/mcheck.log 2>&1; echo "mcheck rc=$?" >> $L/rc.txt
rm -rf "${H:?}/ca2" "${H:?}/ma2"
bash bin/byte-diff-sweep.sh $H/ca2 > $L/ca.log 2>&1; echo "sweep-root rc=$? $(date -u +%FT%TZ)" >> $L/rc.txt
NEW=$(ls test-suite/corpus/pycsl-reference/ | grep -E '^67[5-9][0-9]_.*\.py$' | sed 's/\.py$//' | tr '\n' ' ')
python3 bin/byte-diff-compare.py $V/ca $H/ca2 --new-source $NEW --expect-gone 3289_gen37_dvw_hval_doubled_get_nonmap_noexc_false_claim 4812_gen37_r358_object_attr_noexc 4813_gen37_r358_any_attr_noexc 4825_gen37_r358_any_result_attr_noexc > $L/cmp-root.log 2>&1; echo "cmp-root rc=$?" >> $L/rc.txt
python3 bin/byte-diff-compare.py $V/ca/pyref $H/ca2/pyref --min-files 2000 > $L/cmp-pyref.log 2>&1; echo "cmp-pyref rc=$?" >> $L/rc.txt
python3 bin/byte-diff-compare.py $H/ca $H/ca2 > $L/cmp-root-vs-first.log 2>&1; echo "cmp-root-vs-first-candidate rc=$?" >> $L/rc.txt
bash bin/mirror-emit-sweep.sh $H/ma2 > $L/ma.log 2>&1; echo "sweep-mirror rc=$?" >> $L/rc.txt
python3 bin/byte-diff-compare.py $V/ma $H/ma2 --min-files 50 > $L/cmp-mirror.log 2>&1; echo "cmp-mirror rc=$?" >> $L/rc.txt
$H/codescr.sh $W $H/cs-cand3.tsv $H/claimed.txt > /dev/null; echo "claimed-screen done" >> $L/rc.txt
rm -rf "${H:?}/fw2"
$H/scr.sh $W $H/fw2 --full 3 $(cat $H/full-cand.txt) > /dev/null; echo "witnesses done" >> $L/rc.txt
.venv/bin/python3 bin/check-refusal-witness-coverage.py > $L/rwc.log 2>&1; echo "rwc rc=$?" >> $L/rc.txt
.venv/bin/python3 bin/check-refusal-advice-audited.py > $L/advice.log 2>&1; echo "advice rc=$?" >> $L/rc.txt
python3 bin/doc-coherency.py --check > $L/doc.log 2>&1; echo "doc rc=$?" >> $L/rc.txt
echo "CONFIRMDONE $(date -u +%FT%TZ)" >> $L/rc.txt
