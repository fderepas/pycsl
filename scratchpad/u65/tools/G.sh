#!/bin/bash
# G.sh : one NORMAL heavy job, sequential, on the final commit: compares of the sweeps already in sw/, LG,
# fast planes (teed in full), directive-enforcement, stdlib-modules-verify, rwc, corpus-executes.
W=/home/fabrice/git/pycsl-u65; S=$W/scratchpad/u65/sw; G=$W/scratchpad/u65/logs/G; mkdir -p $G
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "G start $(date -u) $(git -C $W log --oneline -1 | cut -c1-12) $(grep oom_kill $EV)"
cd $W
bash $W/scratchpad/u65/tools/LG.sh $G/lg 2>&1 | sed 's/^/[LG] /'
bash bin/run-soundness-planes.sh 2>&1 | tee $G/planes.txt > /dev/null; echo "planes rc=${PIPESTATUS[0]} $(tail -3 $G/planes.txt | tr '\n' ' ')"
python3 bin/check-directive-enforcement.py > $G/directive.txt 2>&1; echo "directive-enforcement rc=$? $(tail -1 $G/directive.txt)"
python3 bin/check-stdlib-modules-verify.py > $G/stdlib.txt 2>&1; echo "stdlib-modules-verify rc=$? $(tail -1 $G/stdlib.txt)"
python3 bin/check-refusal-witness-coverage.py > $G/rwc.txt 2>&1; echo "rwc rc=$? $(tail -2 $G/rwc.txt | tr '\n' ' ')"
python3 bin/check-corpus-executes.py --verbose > $G/ce.txt 2>&1; echo "corpus-executes rc=$? $(grep -E 'corpus-executes' $G/ce.txt | tail -2 | tr '\n' ' ')"
echo "G end $(date -u) $(grep oom_kill $EV)"
