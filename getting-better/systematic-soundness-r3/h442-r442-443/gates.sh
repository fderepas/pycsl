#!/bin/bash
# h442 gate battery part 1 (sweeps + compares). Run AS ONE heavy.sh job.
H=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/h442
V=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/v10
W=/home/fabrice/git/pycsl-h442
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
L=$H/gates; mkdir -p $L; : > $L/rc.txt
cd $W
echo "start $(git log --oneline -1 | cut -c1-12) $(date -u +%FT%TZ)" >> $L/rc.txt
bash bin/check-self-annotate-sync.sh > $L/sync.log 2>&1; echo "sync rc=$?" >> $L/rc.txt
bash bin/self-annotate-mirror-check.sh > $L/mcheck.log 2>&1; echo "mcheck rc=$?" >> $L/rc.txt
rm -rf "${H:?}/ca" "${H:?}/ma"
bash bin/byte-diff-sweep.sh $H/ca > $L/ca.log 2>&1; echo "sweep-root rc=$? $(date -u +%FT%TZ)" >> $L/rc.txt
NEW=$(ls test-suite/corpus/pycsl-reference/ | grep -E '^67[5-9][0-9]_.*\.py$' | sed 's/\.py$//' | tr '\n' ' ')
python3 bin/byte-diff-compare.py $V/ca $H/ca --new-source $NEW > $L/cmp-root.log 2>&1; echo "cmp-root rc=$?" >> $L/rc.txt
python3 bin/byte-diff-compare.py $V/ca/pyref $H/ca/pyref --min-files 2000 > $L/cmp-pyref.log 2>&1; echo "cmp-pyref rc=$?" >> $L/rc.txt
bash bin/mirror-emit-sweep.sh $H/ma > $L/ma.log 2>&1; echo "sweep-mirror rc=$? $(date -u +%FT%TZ)" >> $L/rc.txt
python3 bin/byte-diff-compare.py $V/ma $H/ma --min-files 50 > $L/cmp-mirror.log 2>&1; echo "cmp-mirror rc=$?" >> $L/rc.txt
echo "SWEEPSDONE $(date -u +%FT%TZ)" >> $L/rc.txt
