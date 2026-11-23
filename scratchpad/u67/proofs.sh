#!/bin/bash
# proofs.sh : u67 sequential proof battery for sertop.py (one heavy.sh slot). Logs -> scratchpad/u67/pr/
T=/home/fabrice/git/pycsl-u67; L=$T/scratchpad/u67/pr; cd $T
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
oom() { grep oom_kill $EV | awk '{print $2}'; }
M=src/self-annotate/src/proof2why3/sertop.py
ORIG=$L/sertop.orig.py; cp $M $ORIG
run() { # tag file args...
  tag=$1; shift; echo "== $tag start $(date -u +%FT%TZ) oom_kill=$(oom)" >> $L/summary.txt
  timeout 3000 python3 src/pycsl/pycsl.py "$@" --import-path src/pycsl --verification-image src/self-annotate/src > $L/$tag.log 2>&1
  rc=$?; v=$(grep -E 'Verification SUCCESS|Verification FAILED|PIPELINE ERROR|non-Valid|Valid:' $L/$tag.log | tail -3 | tr '\n' ' ')
  echo "== $tag end $(date -u +%FT%TZ) rc=$rc oom_kill=$(oom) :: $v" >> $L/summary.txt; }
# 1. --fun of the converted method
run fun $M --fun sertopsession__type_of_batch --keep-mlw
cp ${M%.py}.mlw $L/fun.mlw 2>/dev/null
# 2. whole-file proof of the mirror file
run whole $M --keep-mlw
cp ${M%.py}.mlw $L/whole.mlw 2>/dev/null
# 3. leaf reachability: `#@ assert 1 == 2` at the head of the (single, innermost) body block
python3 - $ORIG $M <<'PY'
import sys; s=open(sys.argv[1]).read()
a="        cwd = self.cwd or Path.cwd()\n"
assert s.count(a)==1; open(sys.argv[2],'w').write(s.replace(a,"        #@ assert 1 == 2\n"+a))
PY
run leaf $M --fun sertopsession__type_of_batch
# 4. mutation: the body writes a field its `assigns \nothing` frame excludes
python3 - $ORIG $M <<'PY'
import sys; s=open(sys.argv[1]).read()
a="        cwd = self.cwd or Path.cwd()\n"
assert s.count(a)==1; open(sys.argv[2],'w').write(s.replace(a,a+"        self.seq = self.seq + 1\n"))
PY
run mut_frame $M --fun sertopsession__type_of_batch
# 5. mutation: the None arm returns the wrong type (int) -> must be rejected
python3 - $ORIG $M <<'PY'
import sys; s=open(sys.argv[1]).read()
a="        cwd = self.cwd or Path.cwd()\n"
assert s.count(a)==1; open(sys.argv[2],'w').write(s.replace(a,"        cwd = self.cwd or self.seq\n"))
PY
run mut_type $M --fun sertopsession__type_of_batch
cp $ORIG $M
# 6. arm reachability on the emitted whole-file .mlw: each match arm replaced by `absurd` must NOT prove
if [ -f $L/whole.mlw ]; then
  for arm in some none; do
    python3 - $L/whole.mlw $L/arm_$arm.mlw $arm <<'PY'
import sys; s=open(sys.argv[1]).read()
a="(match self.cwd with Some _p67 -> _p67 | None -> (ext_path_cwd_op ()) end)"
assert s.count(a)==1, s.count(a)
b={"some":"(match self.cwd with Some _p67 -> absurd | None -> (ext_path_cwd_op ()) end)",
   "none":"(match self.cwd with Some _p67 -> _p67 | None -> absurd end)"}[sys.argv[3]]
open(sys.argv[2],'w').write(s.replace(a,b))
PY
    echo "== arm_$arm start $(date -u +%FT%TZ) oom_kill=$(oom)" >> $L/summary.txt
    for pv in z3 alt-ergo; do
      timeout 900 why3 prove -P $pv -t 30 -a split_vc $L/arm_$arm.mlw > $L/arm_${arm}_$pv.log 2>&1; rc=$?
      echo "== arm_$arm $pv end rc=$rc oom_kill=$(oom) :: $(grep -c ': Valid' $L/arm_${arm}_$pv.log) Valid / $(grep -cE ': (Unknown|Timeout|Invalid|Failure|HighFailure|Step)' $L/arm_${arm}_$pv.log) non-Valid; sertopsession__type_of_batch non-Valid: $(grep sertopsession__type_of_batch $L/arm_${arm}_$pv.log | grep -vc ': Valid')" >> $L/summary.txt
    done
  done
fi
echo "== ALL DONE $(date -u +%FT%TZ)" >> $L/summary.txt
