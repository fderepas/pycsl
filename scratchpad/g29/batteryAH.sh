#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtAR
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteAH.log 2>&1; echo "rc=$?" >> $S/suiteAH.log
grep -E "Results:" $S/suiteAH.log; echo "XPASS lines: $(grep -c XPASS $S/suiteAH.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesAH.log 2>&1; echo "rc=$?" >> $S/planesAH.log
tail -n 2 $S/planesAH.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
