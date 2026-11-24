#!/bin/bash
# w.sh <pid> <logfile> : wait up to 170 s for <pid>; liveness line every ~15 min; print the log tail.
P=$1; F=$2; PR=/home/fabrice/git/pycsl-u64/progress.txt
last=$(stat -c %Y $PR 2>/dev/null || echo 0); [ $(( $(date +%s) - last )) -gt 800 ] && echo "$(date -u) u64: waiting on pid $P ($(basename $F))" >> $PR
timeout 165 bash -c "while kill -0 $P 2>/dev/null; do sleep 5; done"
kill -0 $P 2>/dev/null && echo "RUNNING $(date -u +%H:%M)" || echo "FINISHED"
tail -n ${3:-12} $F
