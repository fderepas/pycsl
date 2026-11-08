#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtAJ
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteAB.log 2>&1; echo "rc=$?" >> $S/suiteAB.log
grep -E "Results:" $S/suiteAB.log; echo "XPASS lines: $(grep -c XPASS $S/suiteAB.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesAB.log 2>&1; echo "rc=$?" >> $S/planesAB.log
tail -n 2 $S/planesAB.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
