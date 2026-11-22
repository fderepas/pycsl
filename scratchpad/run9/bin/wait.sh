#!/bin/bash
# wait.sh [secs<=570] [file-to-watch-for-change] : bounded foreground wait, then a one-screen status
S=${1:-570}; F=$2; m0=$( [ -n "$F" ] && stat -c %Y "$F" 2>/dev/null )
end=$(( $(date +%s) + S )); while [ $(date +%s) -lt $end ]; do sleep 15; [ -n "$F" ] && [ "$(stat -c %Y "$F" 2>/dev/null)" != "$m0" ] && break; done
P=/home/fabrice/git/pycsl; DL=$(cat $P/getting-better/.driver-deadline)
echo "$(date -u +%FT%H:%MZ) left $(( (DL-$(date +%s))/60 )) min; $(grep oom_kill $(cat $P/scratchpad/run9/oompath))"
for t in $(cat $P/scratchpad/run9/agents.txt); do echo "$t: $(tail -n1 $P/../pycsl-$t/progress.txt 2>/dev/null | cut -c1-200)"; done
ps -eo pid,etime,args | grep '[h]eavy/heavy.sh' | awk '{printf "%s %s ", $1, $2; for(i=4;i<=NF&&i<9;i++) printf "%s ", $i; print ""}' | cut -c1-170
