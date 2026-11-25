#!/bin/bash
# run.sh <h|b> <name> [pycsl args]: run pycsl on candidate c/<name>.py in head (h = pycsl-u76 worktree) or base (b = pycsl-u76b, L21 ba48d5888)
T=/home/fabrice/git/pycsl-u76; [ "$1" = b ] && T=/home/fabrice/git/pycsl-u76b
tag=$1; n=$2; shift 2
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u76/scratchpad/u76/tmp
D=/home/fabrice/git/pycsl-u76/scratchpad/u76/c
mkdir -p $D/$tag; cp $D/*.py $D/$tag/ 2>/dev/null
cd $T || exit 2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
OOM0=$(grep oom_kill $EV 2>/dev/null)
timeout 3700 .venv/bin/python3 src/pycsl/pycsl.py $D/$tag/$n.py --import-path src/pycsl --keep-mlw "$@" > $D/$tag/$n.log 2>&1; rc=$?
OOM1=$(grep oom_kill $EV 2>/dev/null)
echo "rc=$rc args=$* oom0=[$OOM0] oom1=[$OOM1]" >> $D/$tag/$n.log
echo "$tag $n rc=$rc $(grep -m1 -oE "All contracts formally proven|PYCSL-[A-Z0-9-]+|Verification FAILED|Verification SUCCESS|line [0-9]+, char[^:]*" $D/$tag/$n.log)"
