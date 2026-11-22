#!/bin/bash
# waitev.sh <max-seconds> : block until a watched run #7 file changes / appears (proof lists, battery summaries, executor branches), or timeout.
R=/home/fabrice/git/pycsl/scratchpad/run9
snap(){ ls --full-time $R/*.txt $R/*.tsv $R/v*/summary.txt  2>/dev/null | awk '{print $6,$7,$9}'; for b in $EXTRA_BRANCHES; do echo "$b $(git -C /home/fabrice/git/pycsl rev-parse $b 2>/dev/null)"; done; }
a=$(snap); end=$(( $(date +%s) + $1 ))
while [ $(date +%s) -lt $end ]; do b=$(snap); [ "$a" != "$b" ] && { diff <(echo "$a") <(echo "$b") | grep '^>' ; exit 0; }; sleep 15; done
echo "TIMEOUT $(date -u +%H:%MZ)"
