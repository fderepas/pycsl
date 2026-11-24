#!/bin/bash
# J2.sh : v1f follow-up: the dependency's own full proof (P/dep75.py) and the program with --deep, base + head.
W=/home/fabrice/git/pycsl-u64; L=$W/scratchpad/u64/logs/J2; mkdir -p $L
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
cd $W; echo "start $(date -u) $(grep oom_kill $EV)"
for t in base:/home/fabrice/git/pycsl-u64-base head:$W; do T=${t#*:}; n=${t%%:*}; echo "## $n $(git -C $T rev-parse --short HEAD)"
  timeout 1500 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py scratchpad/u64/probes/v1f/P/dep75.py > $L/$n-dep75.log 2>&1; echo "dep75 own rc=$? $(grep -E 'Verification|PIPELINE|PYCSL-' $L/$n-dep75.log | head -2 | tr '\n' ' ')"
  timeout 1500 $T/.venv/bin/python3 $T/src/pycsl/pycsl.py --deep scratchpad/u64/probes/v1f/P/prog.py > $L/$n-prog-deep.log 2>&1; echo "prog --deep rc=$? $(grep -E 'Verification|PIPELINE|PYCSL-' $L/$n-prog-deep.log | head -2 | tr '\n' ' ')"
done; echo "end $(date -u) $(grep oom_kill $EV)"
