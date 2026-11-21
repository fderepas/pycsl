#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
R=/home/fabrice/git/pycsl
mkdir -p $S/emit
( cd $S/wt_b && bin/byte-diff-sweep.sh $S/emit/corpus_base && bin/mirror-emit-sweep.sh $S/emit/mirror_base )
( cd $R && bin/byte-diff-sweep.sh $S/emit/corpus_cand && bin/mirror-emit-sweep.sh $S/emit/mirror_cand )
cd $R
echo "== COMPARE corpus"; .venv/bin/python3 bin/byte-diff-compare.py $S/emit/corpus_base $S/emit/corpus_cand; echo rc=$?
echo "== COMPARE pyref"; .venv/bin/python3 bin/byte-diff-compare.py $S/emit/corpus_base/pyref $S/emit/corpus_cand/pyref --min-files 2000; echo rc=$?
echo "== COMPARE mirrors"; .venv/bin/python3 bin/byte-diff-compare.py $S/emit/mirror_base $S/emit/mirror_cand --min-files 45; echo rc=$?
echo EMISSION-DONE
