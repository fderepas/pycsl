#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u75/scratchpad/u75/tmp; mkdir -p "$TMPDIR"
# GATES.sh <outdir> : fidelity + ledger planes (LG), fast planes (full tee), rwc, corpus-executes,
# frontend-only-conformance, \trusted count. cwd = u69 tree root. One NORMAL job.
W=/home/fabrice/git/pycsl-u75; O=$(realpath -m $1); mkdir -p $O; cd $W
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "GATES start $(date -u) $(git rev-parse --short HEAD) $(grep oom_kill $EV)"
bash $W/scratchpad/u73/tools/LG.sh $O/lg 2>&1 | sed 's/^/[LG] /'
bash bin/run-soundness-planes.sh 2>&1 | tee $O/planes.txt > /dev/null; echo "planes rc=${PIPESTATUS[0]} $(tail -3 $O/planes.txt | tr '\n' ' ')"
python3 bin/check-refusal-witness-coverage.py > $O/rwc.txt 2>&1; echo "rwc rc=$? $(tail -2 $O/rwc.txt | tr '\n' ' ')"
python3 bin/check-corpus-executes.py --verbose > $O/ce.txt 2>&1; echo "corpus-executes rc=$? $(tail -3 $O/ce.txt | tr '\n' ' ' | cut -c1-400)"
python3 bin/frontend-only-conformance.py > $O/foc.txt 2>&1; echo "frontend-only-conformance rc=$? $(tail -2 $O/foc.txt | tr '\n' ' ')"
python3 bin/check-dropped-mutation.py > $O/cdm.txt 2>&1; echo "check-dropped-mutation rc=$? $(tail -2 $O/cdm.txt | tr "\n" " ")"
python3 bin/check-vacuous-drivers.py > $O/cvd.txt 2>&1; echo "check-vacuous-drivers rc=$? $(tail -2 $O/cvd.txt | tr "\n" " ")"
echo "GATES end $(date -u) $(grep oom_kill $EV)"
