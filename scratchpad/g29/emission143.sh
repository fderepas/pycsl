#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
R=/home/fabrice/git/pycsl
O=$S/emit143; rm -rf $O; mkdir -p $O
( cd $S/wt_b && bin/byte-diff-sweep.sh $O/corpus_base && bin/mirror-emit-sweep.sh $O/mirror_base )
( cd $S/wt143 && bin/byte-diff-sweep.sh $O/corpus_cand && bin/mirror-emit-sweep.sh $O/mirror_cand )
cd $R
echo "== COMPARE corpus"; .venv/bin/python3 bin/byte-diff-compare.py $O/corpus_base $O/corpus_cand; echo rc=$?
echo "== COMPARE pyref"; .venv/bin/python3 bin/byte-diff-compare.py $O/corpus_base/pyref $O/corpus_cand/pyref --min-files 2000; echo rc=$?
echo "== COMPARE mirrors"; .venv/bin/python3 bin/byte-diff-compare.py $O/mirror_base $O/mirror_cand --min-files 45; echo rc=$?
echo EMISSION-DONE
