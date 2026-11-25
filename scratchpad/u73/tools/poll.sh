#!/bin/bash
# poll.sh <msg> : wait ~170 s, write a liveness line if the last one is older than 14 min, print chain status
P=/home/fabrice/git/pycsl-u73/progress.txt
sleep 170
last=$(stat -c %Y $P); now=$(date +%s)
[ $((now-last)) -gt 840 ] && echo "$(date -u +%FT%TZ) u73: $1" >> $P
L=/home/fabrice/git/pycsl-u73/scratchpad/u73/logs
echo "base: $(tr '\n' ' ' < $L/S-base.txt | cut -c1-300)"; echo "chain1: $(tail -3 $L/chain1.txt | tr '\n' ' ' | cut -c1-400)"
