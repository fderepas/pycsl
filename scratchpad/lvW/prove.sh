#!/bin/bash
# prove.sh <tag> <mirror-rel> [extra pycsl args...] : one heavy pycsl run of a mirror file, logged to scratchpad/lvW/proofs/<tag>.log
T=${TREE:-/home/fabrice/git/pycsl-lvW}; O=/home/fabrice/git/pycsl-lvW/scratchpad/lvW/proofs; mkdir -p $O; tag=$1; f=$2; shift 2
OOM=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; cd $T
ls src/self-annotate/src/$f >/dev/null || exit 2
o0=$(grep oom_kill $OOM 2>/dev/null | awk '{print $2}'); s=$(date +%s); echo "$(date -u +%FT%TZ) START $tag $T $f $* PCC=${PYTHON_CPU_COUNT:-4}" >> $O/summary.txt
PYTHON_CPU_COUNT=${PYTHON_CPU_COUNT:-4} /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh .venv/bin/python3 src/pycsl/pycsl.py src/self-annotate/src/$f --import-path src/pycsl "$@" > $O/$tag.log 2>&1; rc=$?
o1=$(grep oom_kill $OOM 2>/dev/null | awk '{print $2}')
echo "$(date -u +%FT%TZ) END $tag rc=$rc wall=$(( $(date +%s)-s ))s valid=$(grep -c 'Prover result is: Valid' $O/$tag.log) total=$(grep -c 'Prover result is:' $O/$tag.log) nonvalid=$(grep 'Prover result is:' $O/$tag.log | grep -vc ': Valid') $(grep -oE 'Verification (SUCCESS|FAILED)' $O/$tag.log | tail -1) oom_kill=$o0->$o1" >> $O/summary.txt
tail -1 $O/summary.txt
