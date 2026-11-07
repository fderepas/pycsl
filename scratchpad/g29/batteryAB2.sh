#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtAJ
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteAB2.log 2>&1; echo "rc=$?" >> $S/suiteAB2.log
grep -E "Results:" $S/suiteAB2.log; echo "XPASS lines: $(grep -c XPASS $S/suiteAB2.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesAB2.log 2>&1; echo "rc=$?" >> $S/planesAB2.log
tail -n 2 $S/planesAB2.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
