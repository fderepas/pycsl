#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
/home/fabrice/git/pycsl/scratchpad/g29/emitW.sh
cd $S/wtW
timeout 1800 bin/run-soundness-planes.sh > $S/planesWfast.log 2>&1; echo "planes rc=$?"; tail -1 $S/planesWfast.log
timeout 900 bin/run-conformance.sh > $S/confW.log 2>&1; echo "conf rc=$?"
timeout 600 bin/check-self-annotate-sync.sh > /dev/null 2>&1; echo "sync rc=$?"
echo FAST-DONE $(date -u +%H:%M:%SZ)
