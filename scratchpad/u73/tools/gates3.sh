#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u73/scratchpad/u73/tmp; mkdir -p "$TMPDIR"
# gates3.sh : re-gate after the helper contract edit: vacuous-drivers alone, witnesses+helpers full proofs,
# census row re-check, fast planes (teed), rwc, corpus-executes. cwd = u73 tree. One NORMAL job.
U=/home/fabrice/git/pycsl-u73/scratchpad/u73; W=/home/fabrice/git/pycsl-u73; O=$U/logs/GATES3; mkdir -p $O; cd $W
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "GATES3 start $(date -u) $(git rev-parse --short HEAD) $(grep oom_kill $EV)"
python3 bin/check-vacuous-drivers.py --verbose > $O/vac.txt 2>&1; echo "check-vacuous-drivers rc=$? $(grep 'pycsl-reference' $O/vac.txt | head -2 | tr '\n' ' ' | cut -c1-300)"
bash $U/tools/wit.sh p $W $O/w $W | sed 's/^/[w] /'
bash $U/tools/CR.sh > $O/CR-rows.tsv 2>$O/CR.err; diff $O/CR-rows.tsv $U/logs/CR-rows.tsv > /dev/null && echo "census rows identical" || echo "census rows DIFFER"
bash bin/run-soundness-planes.sh 2>&1 | tee $O/planes.txt > /dev/null; echo "planes rc=${PIPESTATUS[0]} $(tail -2 $O/planes.txt | tr '\n' ' ')"
python3 bin/check-refusal-witness-coverage.py > $O/rwc.txt 2>&1; echo "rwc rc=$? $(tail -1 $O/rwc.txt)"
python3 bin/check-corpus-executes.py --verbose > $O/ce.txt 2>&1; echo "corpus-executes rc=$? $(tail -1 $O/ce.txt | cut -c1-200)"
echo "GATES3 end $(date -u) $(grep oom_kill $EV)"
