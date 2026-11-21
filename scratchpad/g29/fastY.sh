#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtY
timeout 1800 bin/run-soundness-planes.sh > $S/planesYfast.log 2>&1; echo "planes rc=$?"; tail -1 $S/planesYfast.log; grep -A2 " RED" $S/planesYfast.log | head -8
timeout 900 bin/run-conformance.sh > $S/confY.log 2>&1; echo "conf rc=$?"
timeout 600 bin/check-self-annotate-sync.sh > /dev/null 2>&1; echo "sync rc=$?"
echo FAST-DONE $(date -u +%H:%M:%SZ)
