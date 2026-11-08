#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtZ
echo PLANES-START $(date -u +%H:%M:%SZ)
timeout 5400 bin/run-soundness-planes.sh --slow > $S/planesR2.log 2>&1; echo "rc=$?" >> $S/planesR2.log
tail -n 2 $S/planesR2.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
