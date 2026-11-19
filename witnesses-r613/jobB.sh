#!/bin/bash
# jobB.sh <snapshot-tree> <out> : the gates. cwd = the tree root (rule 28). Baselines = the L15
# emission (v66 bd-int / mir-int, battery on int67 = 899b6869d's src/bin/test-suite).
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
T=$1; O=$2; mkdir -p $O; S=$O/summary.txt
V=/home/fabrice/git/pycsl/scratchpad/run8/v66
oom(){ grep oom_kill /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events; }
log(){ echo "$(date -u +%H:%MZ) $*" | tee -a $S; }
cd $T || exit 2
log "start tree $(git rev-parse --short HEAD) $(oom)"
python3 -I $T/witnesses-r613/scan-roots.py $T > $O/scan.txt 2>&1; log "scan rc=$?"
bin/byte-diff-sweep.sh $O/bd > $O/bd.log 2>&1; log "sweep rc=$?: $(tail -2 $O/bd.log | tr '\n' ' ')"
NS=$(ls test-suite/corpus/pycsl-reference/1018[0-9]_r613_*.py | xargs -n1 basename | sed 's/\.py$//')
python3 bin/byte-diff-compare.py $V/bd-int $O/bd --new-source $NS > $O/C-root.txt 2>&1; log "C root rc=$?: $(tail -3 $O/C-root.txt | tr '\n' ' ' | cut -c1-500)"
python3 bin/byte-diff-compare.py $V/bd-int/pyref $O/bd/pyref --min-files 2000 > $O/C-pyref.txt 2>&1; log "C pyref rc=$?: $(tail -3 $O/C-pyref.txt | tr '\n' ' ' | cut -c1-500)"
bin/mirror-emit-sweep.sh $O/mir > $O/mir.log 2>&1; log "mirror sweep rc=$?: $(tail -1 $O/mir.log)"
diff -rq $V/mir-int/ $O/mir/ > $O/D.txt 2>&1; log "D mirror: $(ls $O/mir | grep -c mlw) emitted, diff lines $(wc -l < $O/D.txt)"
python3 bin/byte-diff-compare.py $V/mir-int $O/mir --min-files 45 > $O/D-cmp.txt 2>&1; log "D compare rc=$?: $(tail -2 $O/D-cmp.txt | tr '\n' ' ' | cut -c1-300)"
bash bin/check-self-annotate-sync.sh > $O/E-sync.log 2>&1; a=$?; bash bin/self-annotate-mirror-check.sh > $O/E-mc.log 2>&1; b=$?; python3 bin/doc-coherency.py --check > $O/E-doc.log 2>&1; c=$?
log "E fidelity: sync rc=$a mirror-check rc=$b doc rc=$c"
# single-underscore emit dir for the ledger planes (rule 18)
mkdir -p $O/emit_mir; for f in $(cd src/self-annotate/src && find . -name '*.py' | sed 's#^\./##'); do d=$(echo "${f%.py}" | sed 's#/#__#g'); s=$(echo "${f%.py}" | sed 's#/#_#g'); [ -f $O/mir/$d.mlw ] && cp $O/mir/$d.mlw $O/emit_mir/$s.mlw; done
bash bin/run-soundness-planes.sh > $O/F-planes.log 2>&1; log "F fast planes rc=$?: $(tail -3 $O/F-planes.log | tr '\n' ' ' | cut -c1-300)"
python3 bin/check-refusal-witness-coverage.py > $O/P-rwc.log 2>&1; log "refusal-witness-coverage rc=$?: $(tail -2 $O/P-rwc.log | tr '\n' ' ' | cut -c1-250)"
python3 bin/check-assigns-writes-survival.py --emit-dir $O/emit_mir > $O/P-aws.log 2>&1; log "assigns-writes-survival rc=$?: $(tail -2 $O/P-aws.log | tr '\n' ' ' | cut -c1-250)"
python3 bin/check-trusted-frame-honesty.py > $O/P-tfh.log 2>&1; log "trusted-frame-honesty rc=$?: $(tail -2 $O/P-tfh.log | tr '\n' ' ' | cut -c1-250)"
python3 bin/check-getattr-erasure.py > $O/P-gae.log 2>&1; log "getattr-erasure rc=$?: $(tail -2 $O/P-gae.log | tr '\n' ' ' | cut -c1-250)"
python3 bin/frontend-only-conformance.py > $O/P-fo.log 2>&1; log "frontend-only rc=$?: $(tail -1 $O/P-fo.log | cut -c1-200)"
python3 bin/core-only-conformance.py > $O/P-co.log 2>&1; log "core-only rc=$?: $(tail -1 $O/P-co.log | cut -c1-200)"
python3 bin/count-trusted-directives.py > $O/P-ct.log 2>&1; log "count-trusted rc=$?: $(tail -2 $O/P-ct.log | tr '\n' ' ' | cut -c1-200)"
log "ledger: $(git diff --stat 899b6869d -- src/pycsl/proof_axiom_allowlist.py | tail -1) (empty = untouched)"
log "JOBB-DONE $(oom)"
