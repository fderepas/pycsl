#!/bin/bash
# w9.sh [secs]: quiet foreground wait; prints EVENT details or one heartbeat line
S=${1:-165}; cd /home/fabrice/git/pycsl
sig(){ for b in $(git branch --list 'run8-*' --format='%(refname:short)'); do echo "$b $(git log --oneline -1 $b | cut -c1-100)"; done; cat scratchpad/run9/*-proofs.txt scratchpad/run9/*/summary.txt 2>/dev/null; }
A=$(sig); E=$(( $(date +%s) + S ))
while [ $(date +%s) -lt $E ]; do sleep 15; B=$(sig); [ "$B" != "$A" ] && { echo "EVENT:"; diff <(echo "$A") <(echo "$B") | grep '^>'; exit 0; }; done
echo "$(date -u +%H:%MZ) quiet; oom $(grep oom_kill $(cat scratchpad/run9/oompath) | awk '{print $2}'); left $(( ($(cat getting-better/.driver-deadline)-$(date +%s))/3600 ))h"
