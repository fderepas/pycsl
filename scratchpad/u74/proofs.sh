#!/bin/bash
# proofs.sh : u74 sequential proof battery for audit_proof_reverify.py::_to_cache_payload (one heavy.sh NORMAL slot).
T=/home/fabrice/git/pycsl-u74; L=$T/scratchpad/u74/pr; cd $T
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u74/scratchpad/u74/tmp
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
oom() { grep oom_kill $EV | awk '{print $2}'; }
M=src/self-annotate/src/audit_proof_reverify.py
ORIG=$L/apr.orig.py; cp $M $ORIG
F=_to_cache_payload
A='    return {
        "compile_ok": report.compile_ok,'
run() { tag=$1; shift; echo "== $tag start $(date -u +%FT%TZ) oom_kill=$(oom)" >> $L/summary.txt
  timeout 3600 .venv/bin/python3 src/pycsl/pycsl.py "$@" --import-path src/pycsl --verification-image src/self-annotate/src > $L/$tag.log 2>&1
  rc=$?; v=$(grep -E 'Verification SUCCESS|Verification FAILED|PIPELINE ERROR|non-Valid|Valid:|NOT proved|Timeout' $L/$tag.log | tail -3 | tr '\n' ' ')
  echo "== $tag end $(date -u +%FT%TZ) rc=$rc oom_kill=$(oom) :: $v" >> $L/summary.txt; }
for step in ${STEPS:-fun whole leaf mut arms}; do case $step in
fun) run fun $M --fun $F --keep-mlw; cp ${M%.py}.mlw $L/fun.mlw 2>/dev/null ;;
whole) run whole $M --keep-mlw; cp ${M%.py}.mlw $L/whole.mlw 2>/dev/null ;;
leaf) python3 - $ORIG $M "$A" <<'PY'
import sys; s=open(sys.argv[1]).read(); a=sys.argv[3]+"\n"
assert s.count(a)==1; open(sys.argv[2],'w').write(s.replace(a,"    #@ assert 1 == 2\n"+a))
PY
  run leaf $M --fun $F; cp $ORIG $M ;;
mut) python3 - $ORIG $M "$A" <<'PY'
import sys; s=open(sys.argv[1]).read(); a=sys.argv[3]+"\n"
assert s.count(a)==1; open(sys.argv[2],'w').write(s.replace(a,"    report.cached = True\n"+a))
PY
  run mut_frame $M --fun $F; cp $ORIG $M ;;
arms) if [ -f $L/whole.mlw ]; then for arm in outer inner; do
  python3 - $L/whole.mlw $L/arm_$arm.mlw $arm <<'PY'
import sys; s=open(sys.argv[1]).read()
if sys.argv[3]=="outer":
    a="in _u74a1 := HCons"; assert s.count(a)==1; s=s.replace(a,"in absurd; _u74a1 := HCons")
else:
    a="do _u74b1 := HCons"; assert s.count(a)==1; s=s.replace(a,"do absurd; _u74b1 := HCons")
open(sys.argv[2],'w').write(s)
PY
  echo "== arm_$arm start $(date -u +%FT%TZ) oom_kill=$(oom)" >> $L/summary.txt
  for pv in z3 alt-ergo; do timeout 1800 why3 prove -P $pv -t 30 -a split_vc $L/arm_$arm.mlw > $L/arm_${arm}_$pv.log 2>&1; rc=$?
    echo "== arm_$arm $pv end rc=$rc oom_kill=$(oom) :: _to_cache_payload goals: $(grep -c '_to_cache_payload' $L/arm_${arm}_$pv.log) lines, non-Valid: $(grep '_to_cache_payload' $L/arm_${arm}_$pv.log | grep -vc ': Valid')" >> $L/summary.txt; done; done; fi ;;
esac; done
cp $ORIG $M
echo "== ALL DONE $(date -u +%FT%TZ)" >> $L/summary.txt
