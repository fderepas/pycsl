#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
R=/home/fabrice/git/pycsl
O=$S/emN; rm -rf $O; mkdir -p $O
echo "== BASE emit (HEAD) $(date -u +%H:%M:%SZ)"
( cd $R && bin/byte-diff-sweep.sh $O/base && bin/mirror-emit-sweep.sh $O/mbase )
echo "== CAND emit (wtN) $(date -u +%H:%M:%SZ)"
( cd $S/wtN && bin/byte-diff-sweep.sh $O/cand && bin/mirror-emit-sweep.sh $O/mcand )
cd $R
echo "== COMPARE corpus"; .venv/bin/python3 bin/byte-diff-compare.py $O/base $O/cand; echo rc=$?
echo "== COMPARE pyref"; .venv/bin/python3 bin/byte-diff-compare.py $O/base/pyref $O/cand/pyref --min-files 2000; echo rc=$?
echo "== COMPARE mirrors"; .venv/bin/python3 bin/byte-diff-compare.py $O/mbase $O/mcand --min-files 45; echo rc=$?
echo EMISSION-DONE $(date -u +%H:%M:%SZ)
