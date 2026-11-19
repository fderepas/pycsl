#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
O=$S/emitG; rm -rf $O; mkdir -p $O
echo "== CAND emit (wtG instrumented) $(date -u +%H:%M:%SZ)"
( cd $S/wtG && bin/byte-diff-sweep.sh $O/corpus_cand && bin/mirror-emit-sweep.sh $O/mirror_cand )
echo "== ARRAY-ARM hits =="
grep -rl "PYCSLMARKARR" $O/corpus_cand/*.mlw 2>/dev/null | wc -l
grep -rl "PYCSLMARKARR" $O/corpus_cand/pyref/*.mlw 2>/dev/null | wc -l
grep -rl "PYCSLMARKARR" $O/mirror_cand/*.mlw 2>/dev/null | wc -l
echo "== MAP-ARM hits =="
grep -rl "PYCSLMARKMAP" $O/corpus_cand/*.mlw 2>/dev/null | wc -l
grep -rl "PYCSLMARKMAP" $O/corpus_cand/pyref/*.mlw 2>/dev/null | wc -l
grep -rl "PYCSLMARKMAP" $O/mirror_cand/*.mlw 2>/dev/null | wc -l
echo "== FILES =="
grep -rl "PYCSLMARK" $O/corpus_cand/*.mlw $O/corpus_cand/pyref/*.mlw $O/mirror_cand/*.mlw 2>/dev/null | xargs -n1 basename 2>/dev/null | head -40
echo CENSUS-DONE $(date -u +%H:%M:%SZ)
