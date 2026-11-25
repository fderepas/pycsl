#!/bin/bash
# apw.sh: whole-file proof of the moved mirror file audit_proof.py (worktree, cwd = root) + the base-tree param-frame probe
cd /home/fabrice/git/pycsl-u74; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u74/scratchpad/u74/tmp
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events; L=scratchpad/u74/pr
M=src/self-annotate/src/audit_proof.py
bash /home/fabrice/git/pycsl-u74/scratchpad/u74/mut3.sh
echo "== ap_whole start $(date -u +%FT%TZ) $(grep oom_kill $EV)" >> $L/summary.txt
timeout 5400 .venv/bin/python3 src/pycsl/pycsl.py $M --import-path src/pycsl --verification-image src/self-annotate/src --keep-mlw > $L/ap_whole.log 2>&1; rc=$?
cp ${M%.py}.mlw $L/ap_whole.mlw 2>/dev/null
echo "== ap_whole end $(date -u +%FT%TZ) rc=$rc $(grep oom_kill $EV) :: $(grep -E 'Verification SUCCESS|Verification FAILED' $L/ap_whole.log | tail -1)" >> $L/summary.txt
bash scratchpad/u74/frb.sh
echo "== frb (base param-frame probe) $(date -u +%FT%TZ) $(tail -1 scratchpad/u74/rt/frb.log) :: $(grep -E 'Verification SUCCESS|Verification FAILED|PIPELINE' scratchpad/u74/rt/frb.log | tail -1)" >> $L/summary.txt
