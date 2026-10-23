#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtAO
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteAF.log 2>&1; echo "rc=$?" >> $S/suiteAF.log
grep -E "Results:" $S/suiteAF.log; echo "XPASS lines: $(grep -c XPASS $S/suiteAF.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesAF.log 2>&1; echo "rc=$?" >> $S/planesAF.log
tail -n 2 $S/planesAF.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
