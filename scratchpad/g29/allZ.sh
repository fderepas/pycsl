#!/usr/bin/env bash
timeout 1800 /home/fabrice/git/pycsl/scratchpad/g29/emitZ.sh
S=/tmp/claude-1000/-home-fabrice-git-pycsl/69f68cf5-e1c5-4519-a158-7330cb73ad67/scratchpad; R=/home/fabrice/git/pycsl; . $R/scratchpad/g29/env.sh
for n in 1630 1631 1632 1633 1634 1635; do P=$(ls $S/wtZ/test-suite/corpus/pycsl-reference/${n}_*.py); echo "$n HEAD $(timeout 600 $R/.venv/bin/python3 $R/src/pycsl/pycsl.py $P 2>&1 | grep -E "Verification|PIPELINE" | tail -1 | cut -c1-25) DRAFT $(timeout 600 $S/wtZ/.venv/bin/python3 $S/wtZ/src/pycsl/pycsl.py $P 2>&1 | grep -E "Verification|PIPELINE" | tail -1 | cut -c1-25)"; done; rm -f $S/wtZ/test-suite/corpus/pycsl-reference/*.mlw
/home/fabrice/git/pycsl/scratchpad/g29/fastZ.sh
