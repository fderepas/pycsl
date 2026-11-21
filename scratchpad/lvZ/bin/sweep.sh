#!/bin/bash
# sweep.sh <tree> <outdir> : corpus+pyref byte-diff sweep and mirror sweep, cwd = tree root
T=$1; O=$2; mkdir -p $O
OOM=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; cd $T || exit 2
echo "start $(date -u +%FT%TZ) oom=$(grep oom_kill $OOM | awk '{print $2}') head=$(git rev-parse HEAD)" > $O/status
bin/byte-diff-sweep.sh $O/bd > $O/bd.log 2>&1; echo "bd rc=$? $(date -u +%FT%TZ)" >> $O/status
bin/mirror-emit-sweep.sh $O/mir > $O/mir.log 2>&1; echo "mir rc=$? $(date -u +%FT%TZ)" >> $O/status
echo "end $(date -u +%FT%TZ) oom=$(grep oom_kill $OOM | awk '{print $2}')" >> $O/status
