#!/bin/bash
# J.sh : full proofs (PYTHON_CPU_COUNT=2) of the 4 witnesses + probe v1f, base then head; cwd = u64 tree root.
W=/home/fabrice/git/pycsl-u64; L=$W/scratchpad/u64/logs/J; mkdir -p $L
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "start $(date -u) $(grep oom_kill $EV)"
for t in base:/home/fabrice/git/pycsl-u64-base head:$W; do
  echo "## ${t%%:*} $(git -C ${t#*:} rev-parse --short HEAD)"
  $W/scratchpad/u64/tools/wit.sh ${t#*:} $L/pr-${t%%:*} p
  $W/scratchpad/u64/tools/wit.sh ${t#*:} $L/pr-${t%%:*} p scratchpad/u64/probes/v1f/P/prog.py
done
echo "end $(date -u) $(grep oom_kill $EV)"
