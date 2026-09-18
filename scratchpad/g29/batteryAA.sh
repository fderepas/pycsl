#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtAI
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteAA.log 2>&1; echo "rc=$?" >> $S/suiteAA.log
grep -E "Results:" $S/suiteAA.log; echo "XPASS lines: $(grep -c XPASS $S/suiteAA.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesAA.log 2>&1; echo "rc=$?" >> $S/planesAA.log
tail -n 2 $S/planesAA.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
