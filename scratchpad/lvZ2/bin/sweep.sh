#!/bin/bash
# sweep.sh <tree> <outdir> : corpus+pyref byte-diff sweep and mirror sweep (cwd = tree root), then compare
# against int70's emission (scratchpad/run8/v69/{bd-int,mir-int}); comparator once per tree.
T=$1; O=$2; mkdir -p $O
OOM=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
V=/home/fabrice/git/pycsl/scratchpad/run8/v69
oom(){ grep oom_kill $OOM 2>/dev/null | awk '{print $2}'; }
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; cd $T || exit 2
export PYTHON_CPU_COUNT=2
echo "start $(date -u +%FT%TZ) oom=$(oom) head=$(git rev-parse HEAD) cwd=$PWD" > $O/status
bin/byte-diff-sweep.sh $O/bd > $O/bd.log 2>&1; echo "bd rc=$? $(date -u +%FT%TZ) oom=$(oom)" >> $O/status
python3 bin/byte-diff-compare.py $V/bd-int $O/bd > $O/cmp-root.txt 2>&1; echo "cmp-root rc=$?" >> $O/status
python3 bin/byte-diff-compare.py $V/bd-int/pyref $O/bd/pyref > $O/cmp-pyref.txt 2>&1; echo "cmp-pyref rc=$?" >> $O/status
bin/mirror-emit-sweep.sh $O/mir > $O/mir.log 2>&1; echo "mir rc=$? $(date -u +%FT%TZ) oom=$(oom)" >> $O/status
diff -rq $V/mir-int $O/mir > $O/mir-diffq.txt 2>&1; echo "mir-diffq lines=$(wc -l < $O/mir-diffq.txt) n=$(ls $O/mir/*.mlw | wc -l)" >> $O/status
diff -r $V/mir-int $O/mir > $O/mir-diff.txt 2>&1
echo "end $(date -u +%FT%TZ) oom=$(oom)" >> $O/status
