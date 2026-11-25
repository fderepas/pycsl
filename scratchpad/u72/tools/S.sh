#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u72/scratchpad/u72/tmp; mkdir -p $TMPDIR
# S.sh <tree> <outdir> : byte-diff sweep (root + pyref) and mirror sweep of <tree>, cwd = tree root.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
T=$1; O=$2; mkdir -p $O; cd $T || exit 2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "tree $T $(git rev-parse HEAD) start $(date -u) $(grep oom_kill $EV)"
bin/byte-diff-sweep.sh $O/bd > $O/bd.log 2>&1; echo "byte-diff-sweep rc=$? $(tail -2 $O/bd.log | tr '\n' ' ')"
bin/mirror-emit-sweep.sh $O/mir > $O/mir.log 2>&1; echo "mirror-emit-sweep rc=$? $(tail -1 $O/mir.log)"
git status --short src bin test-suite | head
echo "end $(date -u) $(grep oom_kill $EV)"
