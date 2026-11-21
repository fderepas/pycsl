#!/bin/bash
# job3: head gates on the head tree (cwd = tree root): sweeps + compares vs base sweep, fidelity, fast planes, vacuity planes, trusted count
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
U=/home/fabrice/git/pycsl-u56; cd $U || exit 2
G=$U/scratchpad/u56/gates; mkdir -p $G
st(){ echo "$1 rc=$2" >> $G/status.txt; echo "$(date -u) job3 $1 rc=$2" >> $U/progress.txt; }
echo "== $(git rev-parse HEAD) $(date -u)" >> $G/status.txt
W=$U/getting-better/open-routes/witnesses-r616
$W/run-r616.sh /home/fabrice/git/pycsl-u56-base $G/wit-base > $G/wit-base.tsv 2>&1; st wit-base $?
$W/run-r616.sh $U $G/wit-head > $G/wit-head.tsv 2>&1; st wit-head $?
$U/scratchpad/u56/sweep.sh $U $U/scratchpad/u56/sw/head > $G/sweep-head.log 2>&1; st sweep-head $?
B=$U/scratchpad/u56/sw/base; H=$U/scratchpad/u56/sw/head
.venv/bin/python3 bin/byte-diff-compare.py $B/bd $H/bd > $G/C-root.txt 2>&1; st C-root $?
.venv/bin/python3 bin/byte-diff-compare.py $B/bd/pyref $H/bd/pyref --min-files 2000 > $G/C-pyref.txt 2>&1; st C-pyref $?
.venv/bin/python3 bin/byte-diff-compare.py $B/mir $H/mir --min-files 45 > $G/D-mir.txt 2>&1; st D-mir $?
diff -r $B/mir $H/mir > $G/D-mir-diff.txt 2>&1; st D-mir-diff $?
bash bin/check-self-annotate-sync.sh > $G/E-sync.log 2>&1; st E-check-self-annotate-sync $?
bash bin/self-annotate-mirror-check.sh > $G/E-mirror-check.log 2>&1; st E-self-annotate-mirror-check $?
.venv/bin/python3 bin/doc-coherency.py --check > $G/E-doc.log 2>&1; st E-doc-coherency $?
bash bin/run-soundness-planes.sh > $G/P-planes.log 2>&1; st P-planes $?
.venv/bin/python3 bin/check-vacuous-drivers.py > $G/I-check-vacuous-drivers.log 2>&1; st I-check-vacuous-drivers $?
.venv/bin/python3 bin/check-emitted-vacuity.py --emit > $G/I-check-emitted-vacuity.log 2>&1; st I-check-emitted-vacuity $?
.venv/bin/python3 bin/count-trusted-directives.py > $G/I-count-trusted.log 2>&1; st I-count-trusted $?
git diff 57d71f9d3 -- src/pycsl/proof_axiom_allowlist.py | wc -l > $G/L-ledger-diff.txt; st L-ledger-diff-lines-$(cat $G/L-ledger-diff.txt) 0
echo "$(date -u) job3 done" >> $U/progress.txt
