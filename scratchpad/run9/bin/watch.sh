#!/bin/bash
# watch.sh : driver event stream (one line per event). Watches run7 result files, executor branches, base sweep, oom_kill; HOURLY tick.
R=/home/fabrice/git/pycsl/scratchpad/run9; OOM=$(cat $R/oompath)
snap(){ ls --full-time $R/*.txt $R/*.tsv $R/v*/summary.txt $R/base/done.txt 2>/dev/null | grep -v agents.txt | awk '{print $9,$6,$7}'; for b in $(cat $R/branches 2>/dev/null); do echo "branch $b $(git -C /home/fabrice/git/pycsl rev-parse --short $b 2>/dev/null)"; done; echo "oom $(grep oom_kill $OOM | head -1)"; }
a=$(snap); T=$R/.lasttick; [ -f $T ] || date +%s > $T
while true; do sleep 30; b=$(snap); if [ "$a" != "$b" ]; then diff <(echo "$a") <(echo "$b") | grep '^>' | cut -c1-200; a=$b; fi
  n=$(date +%s); if [ $((n-$(cat $T))) -ge 3600 ]; then echo "HOURLY $(date -u +%H:%MZ)"; echo $n > $T; fi; done
