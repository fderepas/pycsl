#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
R=/home/fabrice/git/pycsl
O=$S/emit143
rm -rf $O/corpus_cand2 $O/mirror_cand2
( cd $S/wt143 && bin/byte-diff-sweep.sh $O/corpus_cand2 && bin/mirror-emit-sweep.sh $O/mirror_cand2 )
cd $R
echo "== COMPARE corpus"; .venv/bin/python3 bin/byte-diff-compare.py $O/corpus_base $O/corpus_cand2; echo rc=$?
echo "== COMPARE pyref"; .venv/bin/python3 bin/byte-diff-compare.py $O/corpus_base/pyref $O/corpus_cand2/pyref --min-files 2000; echo rc=$?
echo "== COMPARE mirrors"; .venv/bin/python3 bin/byte-diff-compare.py $O/mirror_base $O/mirror_cand2 --min-files 45; echo rc=$?
echo "== CAND vs CAND(battery C) mirrors"; .venv/bin/python3 bin/byte-diff-compare.py $O/mirror_cand $O/mirror_cand2 --min-files 45; echo rc=$?
echo EMISSION-DONE
cd $S/wt143 && timeout 300 bin/run-conformance.sh 2>&1 | grep -E "OK /|FAIL|determinism"
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suite143b.log 2>&1; echo "rc=$?" >> $S/suite143b.log
grep -E "Results:" $S/suite143b.log; echo "XPASS lines: $(grep -c XPASS $S/suite143b.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planes143b.log 2>&1; echo "rc=$?" >> $S/planes143b.log
tail -n 2 $S/planes143b.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
