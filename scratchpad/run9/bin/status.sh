#!/bin/bash
# status.sh : one-screen driver status
NOW=$(date +%s); ST=$(cat /home/fabrice/git/pycsl/getting-better/.driver-started); DL=$(cat /home/fabrice/git/pycsl/getting-better/.driver-deadline)
echo "$(date -u +%FT%H:%MZ) run hour $(( (NOW-ST)/36 ))e-2 ; left $(( (DL-NOW)/3600 )) h ; oom_kill $(grep oom_kill $(cat /home/fabrice/git/pycsl/scratchpad/run9/oompath) 2>/dev/null | head -1)"
echo "-- heavy.sh jobs (running or queued):"; ps -eo pid,etime,args | grep -E '[h]eavy/heavy.sh' | sed 's|/home/fabrice/git/||g' | cut -c1-180
for t in $(cat /home/fabrice/git/pycsl/scratchpad/run9/agents.txt 2>/dev/null); do W=/home/fabrice/git/pycsl-$t; [ -d $W ] || continue; echo "-- $t: $(git -C $W log --oneline -1 | cut -c1-90) | trusted $(grep -rhF '#@ \trusted' $W/src/self-annotate/src --include='*.py' | wc -l)"; tail -1 $W/progress.txt 2>/dev/null | cut -c1-300; done
