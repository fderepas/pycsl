#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtAA
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteS.log 2>&1; echo "rc=$?" >> $S/suiteS.log
grep -E "Results:" $S/suiteS.log; echo "XPASS lines: $(grep -c XPASS $S/suiteS.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesS.log 2>&1; echo "rc=$?" >> $S/planesS.log
tail -n 2 $S/planesS.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
