#!/bin/bash
U=/home/fabrice/git/pycsl-u67; L=$U/scratchpad/u67; cd $U; source /home/fabrice/git/pycsl/scratchpad/g29/env.sh
EV=/sys/fs/cgroup/user.slice/user-1000.slice/user@1000.service/pycsl.slice/pycsl-heavy.slice/memory.events
echo "fin start $(date -u) $(grep oom_kill $EV)"
for pv in z3 alt-ergo; do timeout 600 why3 prove -P $pv -t 30 -a split_vc $L/pr/arm_none2.mlw > $L/pr/arm_none2_$pv.log 2>&1; echo "arm_none2 $pv rc=$? $(grep -B2 -E 'Prover result is: (Unknown|Timeout|Invalid|Step|Failure)' $L/pr/arm_none2_$pv.log | tr '\n' ' ' | cut -c1-300)"; done
bash bin/run-soundness-planes.sh 2>&1 | tee $L/logs/planes2.txt > /dev/null; echo "planes rc=${PIPESTATUS[0]} $(tail -3 $L/logs/planes2.txt | tr '\n' ' ')"
echo "fin end $(date -u) $(grep oom_kill $EV)"
