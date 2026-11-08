#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtAL
echo FAST-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh > $S/planesALfast.log 2>&1; echo "fast rc=$?"; tail -1 $S/planesALfast.log
echo SLOW-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesALslow.log 2>&1; echo "slow rc=$?"; tail -1 $S/planesALslow.log
echo PLANES-BATTERY-DONE $(date -u +%H:%M:%SZ)
