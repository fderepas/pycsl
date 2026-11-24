#!/bin/bash
# FINAL.sh : in ONE heavy job, on the final snapshot H2: the real _census_row for the witnesses whose row u72
# adds or changes, merged into H2's census, then GATES.sh on H2. cwd = H2 root.
export TMPDIR=/home/fabrice/git/pycsl-u72/scratchpad/u72/tmp; mkdir -p $TMPDIR
U=/home/fabrice/git/pycsl-u72/scratchpad/u72; H2=/home/fabrice/git/pycsl-u72-h2; C=$H2/test-suite/corpus/pycsl-reference
L=$(cd $C && ls 1042[0-3]_*.py 1045[0-6]_*.py 1471_route143_contract_calls_a_helper_the_importer_redefines.py)
echo "FINAL start $(date -u) $(git -C $H2 rev-parse --short HEAD) df: $(df -m /tmp | tail -1)"
for T in /home/fabrice/git/pycsl-u72-b0 /home/fabrice/git/pycsl-u72-u70 $H2; do bash $U/tools/p.sh $T $U/logs/w63-$(basename $T) -- $C/10463_r629_single_lib_attribute_base_ctl.py; done
bash $U/tools/CR.sh $H2 $U/logs/CR-rows.tsv $L
python3 $U/tools/merge_census.py $H2/bin/refusal-witness-census.tsv $U/logs/CR-rows.tsv
GT=$H2 bash $U/tools/GATES.sh $U/logs/GATES
echo "FINAL end $(date -u)"
