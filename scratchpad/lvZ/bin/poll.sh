#!/bin/bash
# poll.sh <pattern> : wait <=170 s for <pattern> in bat1/summary.txt; liveness line every 15 min
S=/home/fabrice/git/pycsl-lvZ/scratchpad/lvZ/bat1/summary.txt; P=/home/fabrice/git/pycsl-lvZ/progress.txt
end=$((SECONDS+140))
while [ $SECONDS -lt $end ] && ! grep -q "$1" $S 2>/dev/null; do sleep 20; done
last=$(stat -c %Y $P); now=$(date +%s)
[ $((now-last)) -gt 840 ] && echo "$(date -u +%FT%TZ) lvZ: waiting on battery bat1 ($(tail -1 $S 2>/dev/null | cut -c1-80 || echo queued))" >> $P
tail -2 $S 2>/dev/null; date -u +%T
