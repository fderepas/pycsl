#!/usr/bin/env bash
timeout 1800 /home/fabrice/git/pycsl/scratchpad/g29/emitAB.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad; R=/home/fabrice/git/pycsl; . $R/scratchpad/g29/env.sh
cd $S/wtAB/test-suite/corpus/pycsl-reference; for n in 1639 1640 1641 1642; do P=$(ls ${n}_*.py); echo "$n DRAFT $(timeout 300 $S/wtAB/.venv/bin/python3 $S/wtAB/src/pycsl/pycsl.py $P 2>&1 | grep -E "Verification|PIPELINE" | tail -1 | cut -c1-25)"; done; rm -f *.mlw
/home/fabrice/git/pycsl/scratchpad/g29/fastAB.sh
