#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtAH
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteZ.log 2>&1; echo "rc=$?" >> $S/suiteZ.log
grep -E "Results:" $S/suiteZ.log; echo "XPASS lines: $(grep -c XPASS $S/suiteZ.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesZ.log 2>&1; echo "rc=$?" >> $S/planesZ.log
tail -n 2 $S/planesZ.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
