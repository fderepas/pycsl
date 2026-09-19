#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtA
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteA.log 2>&1; echo "rc=$?" >> $S/suiteA.log
grep -E "Results:" $S/suiteA.log; echo "XPASS lines: $(grep -c XPASS $S/suiteA.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesA.log 2>&1; echo "rc=$?" >> $S/planesA.log
tail -n 2 $S/planesA.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
