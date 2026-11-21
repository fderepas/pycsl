#!/bin/bash
# battery.sh : ONE heavy job, sequential. S1 spike sweep (lvZs) S2 R sweep (lvZr) S3 census rows (lvZr)
# S4 witness proofs (lvZr) S5 fidelity S6 fast planes S7 individual planes S8 conformance. cwd = tree root.
O=/home/fabrice/git/pycsl-lvZ/scratchpad/lvZ/bat1; mkdir -p $O; S=$O/summary.txt
TS=/home/fabrice/git/pycsl-lvZs; TR=/home/fabrice/git/pycsl-lvZr; B=/home/fabrice/git/pycsl-lvZ/scratchpad/lvZ/bin
OOM=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
oom(){ grep oom_kill $OOM | awk '{print $2}'; }
log(){ echo "$(date -u +%FT%TZ) oom=$(oom) $*" >> $S; }
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PYTHON_CPU_COUNT=2
log "START spike=$(git -C $TS rev-parse --short HEAD) R=$(git -C $TR rev-parse --short HEAD)"
STEPS=${STEPS:-12345678}
if [[ $STEPS == *1* ]]; then $B/sweep.sh $TS $O/sw1; log "S1 spike sweep: $(tr '\n' ' ' < $O/sw1/status)"; fi
if [[ $STEPS == *2* ]]; then $B/sweep.sh $TR $O/swR; log "S2 R sweep: $(tr '\n' ' ' < $O/swR/status)"; fi
cd $TR || exit 2
W=$(ls test-suite/corpus/pycsl-reference/102[45][0-9]_r617*.py)
if [[ $STEPS == *3* ]]; then
  : > $O/census-rows.tsv
  for f in $W; do grep -q '^# pycsl-expected: FAIL' $f || continue
    .venv/bin/python3 -c "import sys; sys.path.insert(0,'bin'); import importlib.util as u; s=u.spec_from_file_location('c','bin/check-refusal-witness-coverage.py'); m=u.module_from_spec(s); s.loader.exec_module(m); sys.stdout.write(m._census_row('.venv/bin/python3', sys.argv[1]))" $f >> $O/census-rows.tsv 2>> $O/census.err
  done
  cat $O/census-rows.tsv >> bin/refusal-witness-census.tsv
  log "S3 census rows: $(wc -l < $O/census-rows.tsv) ($(cut -f2 $O/census-rows.tsv | sort | uniq -c | tr '\n' ' '))"
fi
if [[ $STEPS == *4* ]]; then
  : > $O/wit.tsv
  for mm in hoare typed store; do for f in $W; do b=$(basename $f .py); lg=$O/wit.$b.$mm.log; o0=$(oom)
    timeout 1200 .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl --memory-model $mm > $lg 2>&1; rc=$?
    echo -e "$b\t$mm\trc=$rc\toom=$o0->$(oom)\t$(grep -m1 '^# pycsl-expected:' $f | sed 's/.*: *//')\t$(grep -oE 'Verification SUCCESS|Verification FAILED|PYCSL-R[0-9]+[A-Z0-9-]*|L3-tc ✗|PIPELINE ERROR' $lg | head -1)\tvalid=$(grep -c 'Prover result is: Valid' $lg)/$(grep -c 'Prover result is:' $lg)" >> $O/wit.tsv
  done; done
  log "S4 witnesses: $(cut -f5,6 $O/wit.tsv | sort | uniq -c | tr '\n' ' ')"
fi
if [[ $STEPS == *5* ]]; then
  bash bin/check-self-annotate-sync.sh > $O/E-sync.log 2>&1; e1=$?
  bash bin/self-annotate-mirror-check.sh > $O/E-mc.log 2>&1; e2=$?
  python3 bin/doc-coherency.py --check > $O/E-doc.log 2>&1; e3=$?
  log "S5 fidelity sync=$e1 mirror-check=$e2 doc=$e3"
fi
if [[ $STEPS == *6* ]]; then
  bash bin/run-soundness-planes.sh 2>&1 | tee $O/planes.log > /dev/null; rp=${PIPESTATUS[0]}
  log "S6 fast planes rc=$rp: $(tail -3 $O/planes.log | tr '\n' ' ' | cut -c1-300)"
fi
if [[ $STEPS == *7* ]]; then
  E1=$O/emit1; rm -rf "${E1:?}"; mkdir -p $E1
  for f in $O/swR/mir/*.mlw; do n=$(basename $f); n=$(echo $n | sed -E 's/^(frontend|module6_whyml|proof2why3)__/\1_/'); cp $f $E1/$n; done
  for p in check-refusal-witness-coverage check-getattr-erasure check-claim-vacuity; do python3 bin/$p.py > $O/pl.$p.log 2>&1; echo "$p rc=$?" >> $O/planes-ind.txt; done
  for p in check-assigns-writes-survival check-trusted-frame-honesty count-trusted-directives; do python3 bin/$p.py --emit-dir $E1 > $O/pl.$p.log 2>&1; echo "$p rc=$?" >> $O/planes-ind.txt; done
  log "S7 planes: $(tr '\n' ' ' < $O/planes-ind.txt)"
fi
if [[ $STEPS == *8* ]]; then
  python3 bin/frontend-only-conformance.py > $O/fe-conf.log 2>&1; c1=$?
  python3 bin/core-only-conformance.py > $O/core-conf.log 2>&1; c2=$?
  log "S8 conformance fe=$c1 core=$c2"
fi
log "BATTERY-DONE"
