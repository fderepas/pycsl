#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtY
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteQ.log 2>&1; echo "rc=$?" >> $S/suiteQ.log
grep -E "Results:" $S/suiteQ.log; echo "XPASS lines: $(grep -c XPASS $S/suiteQ.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesQ.log 2>&1; echo "rc=$?" >> $S/planesQ.log
tail -n 2 $S/planesQ.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
