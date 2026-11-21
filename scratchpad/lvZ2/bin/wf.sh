#!/bin/bash
# wf.sh <tree> <out> : whole-file proof of the mirror pycsl.py (launch with HEAVY_LOW=1); cwd = tree root
T=$1; O=$2; mkdir -p $O
OOM=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
oom(){ grep oom_kill $OOM 2>/dev/null | awk '{print $2}'; }
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
cd $T || exit 2; ls src/self-annotate/src/pycsl.py || exit 2
o0=$(oom); s=$(date +%s); echo "start $(date -u +%FT%TZ) oom=$o0 head=$(git rev-parse --short HEAD)" > $O/wf.status
timeout 9000 .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/pycsl.py --import-path $T/src/pycsl > $O/wf.log 2>&1; rc=$?
rm -f src/self-annotate/src/pycsl.mlw
echo "end $(date -u +%FT%TZ) rc=$rc secs=$(( $(date +%s)-s )) oom=$o0->$(oom) valid=$(grep -c 'Prover result is: Valid' $O/wf.log)/$(grep -c 'Prover result is:' $O/wf.log) $(grep -oE 'Verification (SUCCESS|FAILED)' $O/wf.log | tail -1)" >> $O/wf.status
