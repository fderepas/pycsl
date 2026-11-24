#!/bin/bash
# P1.sh: full proofs: rt84 + u76 probes head (worktree) and base (L21), witnesses at head, mirror whole-file proofs of audit_proof_reverify.py / audit_proof.py at head
U=/home/fabrice/git/pycsl-u76/scratchpad/u76
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "P1 start $(date -u) $(grep oom_kill $EV)"
$U/p.sh h f1 f2 f3 e1 e2 e3 e4 e5 e6 e7 e8 p1 p2 p3 p4 k3 k5 k8 fr fr2 m634 x634 m634b x634b x634p m634d x634d m634e x634e x634f m634n x634n
$U/p.sh b f1 f2 f3 e1 e3 p1 k1 k2 k3 k8 fr fr2 m634 x634 m634d x634d x634b x634p x634n
$U/pw.sh /home/fabrice/git/pycsl-u76
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=$U/tmp
mkdir -p $U/pr; cd /home/fabrice/git/pycsl-u76 || exit 2
for m in audit_proof_reverify audit_proof; do o0=$(grep oom_kill $EV); s=src/self-annotate/src/$m.py; rm -f src/self-annotate/src/$m.mlw
  timeout 5400 .venv/bin/python3 src/pycsl/pycsl.py $s --import-path src/pycsl --verification-image src/self-annotate/src --keep-mlw > $U/pr/$m.whole.log 2>&1; rc=$?
  [ -f src/self-annotate/src/$m.mlw ] && mv src/self-annotate/src/$m.mlw $U/pr/$m.whole.mlw
  echo "whole $m rc=$rc $(grep -m1 -oE 'All contracts formally proven|Verification FAILED|PIPELINE ERROR' $U/pr/$m.whole.log) [$o0 / $(grep oom_kill $EV)] $(date -u)"
done
echo "P1 end $(date -u) $(grep oom_kill $EV)"
