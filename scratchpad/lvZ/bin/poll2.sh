#!/bin/bash
P=$(cat /home/fabrice/git/pycsl-lvZ/scratchpad/lvZ/bat2.pid); L=/home/fabrice/git/pycsl-lvZ/progress.txt
end=$((SECONDS+140)); while kill -0 $P 2>/dev/null && [ $SECONDS -lt $end ]; do sleep 10; done
[ $(( $(date +%s) - $(stat -c %Y $L) )) -gt 840 ] && echo "$(date -u +%FT%TZ) lvZ: waiting on bat2 (10251 x3 re-proof)" >> $L
cat /home/fabrice/git/pycsl-lvZ/scratchpad/lvZ/bat2/wit.tsv 2>/dev/null; kill -0 $P 2>/dev/null && echo running; date -u +%T
