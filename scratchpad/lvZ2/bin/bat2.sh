#!/bin/bash
# bat2.sh <tree> <outdir> [STEPS] : ONE heavy job, sequential gates on a snapshot tree (cwd = tree root).
# S1 sweep (corpus/pyref/mirror vs v69 int) S2 census rows S3 witnesses x3 S4 --fun/leaf/mutant
# S5 fidelity S6 fast planes S7 individual planes S8 conformance
T=$1; O=$2; STEPS=${3:-12345678}; mkdir -p $O; S=$O/summary.txt
B=/home/fabrice/git/pycsl-lvZ2/scratchpad/lvZ2
OOM=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
oom(){ grep oom_kill $OOM 2>/dev/null | awk '{print $2}'; }
log(){ echo "$(date -u +%FT%TZ) oom=$(oom) $*" >> $S; }
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PYTHON_CPU_COUNT=2
ls $T/src/pycsl/pycsl.py || exit 2
log "START tree=$T head=$(git -C $T rev-parse --short HEAD) steps=$STEPS"
if [[ $STEPS == *1* ]]; then $B/bin/sweep.sh $T $O/sw; log "S1 sweep: $(tr '\n' ' ' < $O/sw/status)"; fi
cd $T || exit 2
R=test-suite/corpus/pycsl-reference
W=$(ls $R/1028[0-9]_lvz2_*.py $R/1029[0-6]_lvz2_*.py 2>/dev/null)
if [[ $STEPS == *2* ]]; then
  : > $O/census-rows.tsv
  for f in $W; do grep -q '^# pycsl-expected: FAIL' $f || continue
    .venv/bin/python3 -c "import sys; sys.path.insert(0,'bin'); import importlib.util as u; s=u.spec_from_file_location('c','bin/check-refusal-witness-coverage.py'); m=u.module_from_spec(s); s.loader.exec_module(m); sys.stdout.write(m._census_row('.venv/bin/python3', sys.argv[1]))" $f >> $O/census-rows.tsv 2>> $O/census.err
  done
  cat $O/census-rows.tsv >> bin/refusal-witness-census.tsv
  log "S2 census rows: $(wc -l < $O/census-rows.tsv) ($(cut -f2 $O/census-rows.tsv | sort | uniq -c | tr '\n' ' '))"
fi
if [[ $STEPS == *3* ]]; then
  : > $O/wit.tsv
  WP="$W $(ls $R/1014[0-5]_lvx_*.py $R/1025[12]_r617_*.py $R/10205_r614_*.py)"
  for mm in hoare typed store; do for f in $WP; do b=$(basename $f .py); lg=$O/wit.$b.$mm.log; o0=$(oom)
    timeout 1200 .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl --memory-model $mm > $lg 2>&1; rc=$?
    echo -e "$b\t$mm\trc=$rc\toom=$o0->$(oom)\t$(grep -m1 '^# pycsl-expected:' $f | sed 's/.*: *//')\t$(grep -oE 'Verification SUCCESS|Verification FAILED|PYCSL-R[0-9]+[A-Z0-9-]*|L3-tc ✗|PIPELINE ERROR' $lg | head -1)\tvalid=$(grep -c 'Prover result is: Valid' $lg)/$(grep -c 'Prover result is:' $lg)" >> $O/wit.tsv
  done; done
  log "S3 witnesses: $(cut -f5,6 $O/wit.tsv | sort | uniq -c | tr '\n' ' ')"
fi
if [[ $STEPS == *4* ]]; then
  F=src/self-annotate/src/pycsl.py; cp $F $O/pycsl.mirror.bak
  o0=$(oom); timeout 9000 .venv/bin/python3 src/pycsl/pycsl.py $F --import-path $T/src/pycsl --fun _sha256_file > $O/fun.log 2>&1; echo "rc=$? oom=$o0->$(oom)" >> $O/fun.log
  python3 - $F leaf <<'PY'
import sys; p,k=sys.argv[1:]; s=open(p).read()
o="    _p = Path(path)\n    return hashlib.sha256(_p.read_bytes()).hexdigest()\n"
assert s.count(o)==1
n=("    _p = Path(path)\n    #@ assert 1 == 2\n    return hashlib.sha256(_p.read_bytes()).hexdigest()\n" if k=="leaf"
   else "    _n7 = 7 // len(path)\n"+o)
open(p,"w").write(s.replace(o,n))
PY
  o0=$(oom); timeout 9000 .venv/bin/python3 src/pycsl/pycsl.py $F --import-path $T/src/pycsl --fun _sha256_file > $O/leaf.log 2>&1; echo "rc=$? oom=$o0->$(oom)" >> $O/leaf.log
  cp $O/pycsl.mirror.bak $F
  python3 - $F mut <<'PY'
import sys; p,k=sys.argv[1:]; s=open(p).read()
o="    _p = Path(path)\n    return hashlib.sha256(_p.read_bytes()).hexdigest()\n"
assert s.count(o)==1
open(p,"w").write(s.replace(o,"    _n7 = 7 // len(path)\n"+o))
PY
  o0=$(oom); timeout 9000 .venv/bin/python3 src/pycsl/pycsl.py $F --import-path $T/src/pycsl --fun _sha256_file > $O/mut.log 2>&1; echo "rc=$? oom=$o0->$(oom)" >> $O/mut.log
  cp $O/pycsl.mirror.bak $F; rm -f src/self-annotate/src/pycsl.mlw
  log "S4 fun: $(grep -oE 'Verification (SUCCESS|FAILED)' $O/fun.log | tail -1) $(tail -1 $O/fun.log) valid=$(grep -c 'Prover result is: Valid' $O/fun.log)/$(grep -c 'Prover result is:' $O/fun.log); leaf: $(grep -oE 'Verification (SUCCESS|FAILED)' $O/leaf.log | tail -1); mut: $(grep -oE 'Verification (SUCCESS|FAILED)' $O/mut.log | tail -1); diff-restored=$(cmp -s $F $O/pycsl.mirror.bak && echo same)"
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
  for f in $O/sw/mir/*.mlw; do n=$(basename $f); n=$(echo $n | sed -E 's/^(frontend|module6_whyml|proof2why3)__/\1_/'); cp $f $E1/$n; done
  : > $O/planes-ind.txt
  for p in check-refusal-witness-coverage check-getattr-erasure check-claim-vacuity check-assumed-facts; do python3 bin/$p.py > $O/pl.$p.log 2>&1; echo "$p rc=$?" >> $O/planes-ind.txt; done
  for p in check-assigns-writes-survival check-trusted-frame-honesty count-trusted-directives; do python3 bin/$p.py --emit-dir $E1 > $O/pl.$p.log 2>&1; echo "$p rc=$?" >> $O/planes-ind.txt; done
  log "S7 planes: $(tr '\n' ' ' < $O/planes-ind.txt)"
fi
if [[ $STEPS == *8* ]]; then
  python3 bin/frontend-only-conformance.py > $O/fe-conf.log 2>&1; c1=$?
  python3 bin/core-only-conformance.py > $O/core-conf.log 2>&1; c2=$?
  log "S8 conformance fe=$c1 core=$c2"
fi
log "BATTERY-DONE"
