#!/bin/bash
# w8.sh [secs] : foreground bounded wait (<= secs, default 570) until an executor branch head or a driver proof file changes; then print status
S=${1:-570}; cd /home/fabrice/git/pycsl
sig(){ for b in $(git branch --list 'run8-*' --format='%(refname:short)'); do git rev-parse $b; done; cat scratchpad/run9/*-proofs.txt scratchpad/run9/*/summary.txt 2>/dev/null | md5sum; }
A=$(sig); E=$(( $(date +%s) + S ))
while [ $(date +%s) -lt $E ]; do sleep 30; [ "$(sig)" != "$A" ] && { echo "EVENT"; break; }; done
bash scratchpad/run9/bin/status.sh 2>&1 | grep -v shell-snapshots | cut -c1-180
