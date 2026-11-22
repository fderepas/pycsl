#!/bin/bash
# w.sh [secs<=165] : foreground wait for a driver event; persistent snapshot so nothing is missed between calls.
R=/home/fabrice/git/pycsl/scratchpad/run9; OOM=$(cat $R/oompath); S=$R/.wsnap; T=$R/.lasttick; MAX=${1:-165}
snap(){ ls --full-time $R/*.txt $R/*.tsv $R/v*/summary.txt $R/base/done.txt 2>/dev/null | grep -v agents.txt | awk '{print $9,$6,$7}'; for b in $(cat $R/branches 2>/dev/null); do echo "branch $b $(git -C /home/fabrice/git/pycsl rev-parse --short $b 2>/dev/null)"; done; echo "oom $(grep oom_kill $OOM | head -1)"; }
[ -f $S ] || snap > $S; [ -f $T ] || date +%s > $T
end=$(( $(date +%s) + MAX ))
while [ $(date +%s) -lt $end ]; do
  b=$(snap); if [ "$(cat $S)" != "$b" ]; then diff $S <(echo "$b") | grep '^>' | cut -c1-200; echo "$b" > $S; exit 0; fi
  n=$(date +%s); if [ $((n-$(cat $T))) -ge 3600 ]; then echo "HOURLY $(date -u +%H:%MZ)"; echo $n > $T; exit 0; fi
  sleep 10
done
echo "quiet $(date -u +%H:%MZ)"
