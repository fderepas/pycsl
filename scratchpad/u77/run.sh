#!/bin/bash
# run.sh <h|b> <stem> [pycsl args]: run pycsl on c/<stem>.py from tree root; log in c/<tag>/<stem>[.q].log
T=/home/fabrice/git/pycsl-u77; [ "$1" = b ] && T=/home/fabrice/git/pycsl-u77b
tag=$1; n=$2; shift 2
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u77/scratchpad/u77/tmp
S=/home/fabrice/git/pycsl-u77/scratchpad/u77/c; D=$S/$tag/$n
mkdir -p $D; cp $S/$n.py $D/
sfx="${SFX:-}"; case " $* " in *" --no-proof "*) sfx="$sfx.q";; esac
cd $T
OOM0=$(grep oom_kill /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events 2>/dev/null)
timeout 3700 .venv/bin/python3 src/pycsl/pycsl.py $D/$n.py --import-path $D --keep-mlw "$@" > $D/$n$sfx.log 2>&1; rc=$?
OOM1=$(grep oom_kill /sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events 2>/dev/null)
echo "rc=$rc args=$* oom0=[$OOM0] oom1=[$OOM1]" >> $D/$n$sfx.log
