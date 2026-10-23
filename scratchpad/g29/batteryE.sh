#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
R=/home/fabrice/git/pycsl
O=$S/emitE; rm -rf $O; mkdir -p $O
( cd $S/wt150 && bin/byte-diff-sweep.sh $O/corpus_cand && bin/mirror-emit-sweep.sh $O/mirror_cand )
cd $R
B=$S/emitD
echo "== COMPARE corpus"; .venv/bin/python3 bin/byte-diff-compare.py $B/corpus_cand $O/corpus_cand; echo rc=$?
echo "== COMPARE pyref"; .venv/bin/python3 bin/byte-diff-compare.py $B/corpus_cand/pyref $O/corpus_cand/pyref --min-files 2000; echo rc=$?
echo "== COMPARE mirrors"; .venv/bin/python3 bin/byte-diff-compare.py $B/mirror_cand $O/mirror_cand --min-files 45; echo rc=$?
echo EMISSION-DONE $(date -u +%H:%M:%SZ)
cd $S/wt150
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteE.log 2>&1; echo "rc=$?" >> $S/suiteE.log
grep -E "Results:" $S/suiteE.log; echo "XPASS lines: $(grep -c XPASS $S/suiteE.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesE.log 2>&1; echo "rc=$?" >> $S/planesE.log
tail -n 2 $S/planesE.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
