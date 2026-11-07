#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
R=/home/fabrice/git/pycsl
O=$S/emitAJ; rm -rf $O; mkdir -p $O
( cd $S/wtAJ && bin/byte-diff-sweep.sh $O/corpus_cand && bin/mirror-emit-sweep.sh $O/mirror_cand )
cd $R
B=$S/emitAI
echo "== COMPARE corpus"; .venv/bin/python3 bin/byte-diff-compare.py $B/corpus_cand $O/corpus_cand; echo rc=$?
echo "== COMPARE pyref"; .venv/bin/python3 bin/byte-diff-compare.py $B/corpus_cand/pyref $O/corpus_cand/pyref --min-files 2000; echo rc=$?
echo "== COMPARE mirrors"; .venv/bin/python3 bin/byte-diff-compare.py $B/mirror_cand $O/mirror_cand --min-files 45; echo rc=$?
echo EMISSION-DONE $(date -u +%H:%M:%SZ)
