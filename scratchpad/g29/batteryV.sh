#!/usr/bin/env bash
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad
cd $S/wtAD
echo SUITE-START $(date -u +%H:%M:%SZ)
bin/run-reference-tests.sh > $S/suiteV.log 2>&1; echo "rc=$?" >> $S/suiteV.log
grep -E "Results:" $S/suiteV.log; echo "XPASS lines: $(grep -c XPASS $S/suiteV.log)"
echo PLANES-START $(date -u +%H:%M:%SZ)
bin/run-soundness-planes.sh --slow > $S/planesV.log 2>&1; echo "rc=$?" >> $S/planesV.log
tail -n 2 $S/planesV.log
echo BATTERY-DONE $(date -u +%H:%M:%SZ)
