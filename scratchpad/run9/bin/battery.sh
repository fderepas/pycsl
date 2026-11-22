#!/bin/bash
# battery.sh <name> <int-tree> <base-tree> [witness-dir ...]
# Driver integration battery (run #7). Every heavy step through heavy.sh, sequential. Output in scratchpad/run9/<name>/.
# Steps: A new corpus files full verdict vs header; B witnesses x 3 models (--no-proof); C corpus byte-diff root+pyref
# (int vs base, compared twice); D mirror sweep diff; E fidelity; F --slow planes. Writes STEP lines to summary.txt.
N=$1; T=$2; B=$3; shift 3
H=/home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh
O=/home/fabrice/git/pycsl/scratchpad/run9/$N; mkdir -p $O; S=$O/summary.txt; STEPS=${STEPS:-ABCDEF}; [ "$STEPS" = ABCDEF ] && : > $S
SP=/home/fabrice/git/pycsl/scratchpad/run9/bin
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
log(){ echo "$(date -u +%H:%MZ) $*" >> $S; }
BC=$(git -C $B rev-parse HEAD)
NEW=$(cd $T && git diff --name-only --diff-filter=A $BC HEAD -- test-suite/corpus/pycsl-reference/ | grep '\.py$')
# A
if [[ $STEPS == *A* ]]; then
: > $O/A.tsv
# one heavy job for all new files (a per-file heavy.sh call waits behind every queued sweep)
[ -n "$NEW" ] && $H $SP/full.sh $T $NEW > $O/A.raw 2>&1
for f in $NEW; do exp=$(grep -m1 '^# pycsl-expected:' $T/$f | sed 's/.*: *//'); 
  r=$(grep -P "^$(basename $f)\t" $O/A.raw | cut -f2); echo -e "$(basename $f)\t$exp\t$r" >> $O/A.tsv; done
nA=$(wc -l < $O/A.tsv); badA=$(awk -F'\t' '($2=="PASS" && $3!~/SUCCESS/) || ($2=="FAIL" && $3~/^Verification SUCCESS *$/)' $O/A.tsv | wc -l)
log "A new corpus files: $nA, unexpected: $badA"
fi
# B
if [[ $STEPS == *B* ]]; then
: > $O/B.tsv
for d in "$@"; do fs=$(ls $d/*.py 2>/dev/null); [ -z "$fs" ] && continue
  HEAVY_QUICK=1 $H bash -c "for mm in hoare typed store; do $SP/wit.sh $T \$mm $(echo $fs); done" >> $O/B.tsv; done
nB=$(wc -l < $O/B.tsv); emB=$(grep -c 'EMITTED$' $O/B.tsv)
log "B witness runs: $nB, EMITTED (not refused front-end; check proofs): $emB"
fi
# C
if [[ $STEPS == *C* ]]; then
rm -rf "${O:?}/bd-base" "${O:?}/bd-int"; rm -f "${O:?}/bd-base"
if [ -n "$BASE_BD" ]; then ln -sfn $BASE_BD $O/bd-base; else (cd $B && $H bin/byte-diff-sweep.sh $O/bd-base > $O/bd-base.log 2>&1); fi
(cd $T && $H bin/byte-diff-sweep.sh $O/bd-int > $O/bd-int.log 2>&1)
NS=$(for f in $NEW; do basename $f .py; done)
python3 /home/fabrice/git/pycsl/bin/byte-diff-compare.py $O/bd-base $O/bd-int --new-source $NS > $O/C-root.txt 2>&1; rr=$?
python3 /home/fabrice/git/pycsl/bin/byte-diff-compare.py $O/bd-base/pyref $O/bd-int/pyref > $O/C-pyref.txt 2>&1; rp=$?
log "C byte-diff root rc=$rr: $(tail -3 $O/C-root.txt | tr '\n' ' ' | cut -c1-300)"
log "C byte-diff pyref rc=$rp: $(tail -3 $O/C-pyref.txt | tr '\n' ' ' | cut -c1-300)"
fi
# D
if [[ $STEPS == *D* ]]; then
rm -rf "${O:?}/mir-base" "${O:?}/mir-int"; rm -f "${O:?}/mir-base"
if [ -n "$BASE_MIR" ]; then ln -sfn $BASE_MIR $O/mir-base; else (cd $B && $H bin/mirror-emit-sweep.sh $O/mir-base > $O/mir-base.log 2>&1); fi
(cd $T && $H bin/mirror-emit-sweep.sh $O/mir-int > $O/mir-int.log 2>&1)
diff -rq $O/mir-base/ $O/mir-int/ > $O/D.txt 2>&1
log "D mirror: $(ls $O/mir-int | grep -c mlw) emitted, diff lines $(wc -l < $O/D.txt): $(cat $O/D.txt | tr '\n' ' ' | cut -c1-400)"
fi
# E
if [[ $STEPS == *E* ]]; then
(cd $T && bash bin/check-self-annotate-sync.sh > $O/E-sync.log 2>&1; echo "sync rc=$?" > $O/E.txt; bash bin/self-annotate-mirror-check.sh > $O/E-mc.log 2>&1; echo "mirror-check rc=$?" >> $O/E.txt; python3 bin/doc-coherency.py --check > $O/E-doc.log 2>&1; echo "doc rc=$?" >> $O/E.txt)
log "E fidelity: $(cat $O/E.txt | tr '\n' ' ')"
fi
# F
if [[ $STEPS == *F* ]]; then
(cd $T && $H bash bin/run-soundness-planes.sh --slow > $O/F-planes.log 2>&1); rf=$?
log "F --slow planes rc=$rf: $(tail -4 $O/F-planes.log | tr '\n' ' ' | cut -c1-300)"
fi
log "BATTERY-DONE"
