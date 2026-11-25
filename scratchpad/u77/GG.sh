#!/bin/bash
# GG.sh: census rows (real _census_row) for the 4 new FAIL witnesses in pycsl-u77h, witness proofs on the snapshot, then G.sh gates.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2 TMPDIR=/home/fabrice/git/pycsl-u77/scratchpad/u77/tmp
U=/home/fabrice/git/pycsl-u77/scratchpad/u77; H=/home/fabrice/git/pycsl-u77h; C=$H/test-suite/corpus/pycsl-reference
cd $H || exit 2
.venv/bin/python3 $U/cen_rows.py $C/10531_*.py $C/10533_*.py $C/10534_*.py $C/10536_*.py > $U/logs/CEN.out 2>&1; echo "cen rc=$?"
$U/wit.sh hs:$H
bash $U/G.sh
echo GGDONE
