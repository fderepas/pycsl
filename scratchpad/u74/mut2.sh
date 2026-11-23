#!/bin/bash
# mut2.sh: --fun proof of the mutant (string-field index) in the scratch tree st/ (mirror restored after)
L=/home/fabrice/git/pycsl-u74/scratchpad/u74; T=$L/st; cd $T
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=$L/tmp
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
f=src/self-annotate/src/audit_proof_reverify.py; cp /home/fabrice/git/pycsl-u74/$f $L/pr/mut2.orig.py; cp $L/v/mut2.py $f
echo "== mut2 start $(date -u +%FT%TZ) $(grep oom_kill $EV)" >> $L/pr/summary.txt
timeout 1800 /home/fabrice/git/pycsl/.venv/bin/python3 src/pycsl/pycsl.py $f --fun _to_cache_payload --import-path $T/src/pycsl --verification-image $T/src/self-annotate/src --keep-mlw > $L/pr/mut2.log 2>&1; rc=$?
echo "== mut2 end $(date -u +%FT%TZ) rc=$rc $(grep oom_kill $EV) :: $(grep -E 'Verification SUCCESS|Verification FAILED' $L/pr/mut2.log | tail -1)" >> $L/pr/summary.txt
cp ${f%.py}.mlw $L/pr/mut2.mlw 2>/dev/null; cp $L/pr/mut2.orig.py $f
