#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u73/scratchpad/u73/tmp; mkdir -p "$TMPDIR"
# chain2.sh : (one NORMAL job) final gate sweeps: base2 = main b959bb1b2 (L21), h2 = e0e1dad26 (final src), compare;
# census rows (real _census_row) for 10470-10474 appended; GATES on the u73 worktree.
U=/home/fabrice/git/pycsl-u73/scratchpad/u73; W=/home/fabrice/git/pycsl-u73
echo "chain2 start $(date -u)"
bash $U/tools/S.sh /home/fabrice/git/pycsl-u73-b2 $U/logs/G/base2
bash $U/tools/S.sh /home/fabrice/git/pycsl-u73-h2 $U/logs/G/h2
bash $U/tools/CMP2.sh h2 base2
bash $U/tools/CR.sh > $U/logs/CR-rows.tsv 2>$U/logs/CR-rows.err; echo "CR rc=$? rows=$(wc -l < $U/logs/CR-rows.tsv)"
cd $W; if [ "$(wc -l < $U/logs/CR-rows.tsv)" = 5 ] && ! grep -q '^10470_' bin/refusal-witness-census.tsv; then cat $U/logs/CR-rows.tsv >> bin/refusal-witness-census.tsv; echo "census rows appended"; fi
bash $U/tools/GATES.sh $U/logs/GATES 2>&1
echo "chain2 end $(date -u)"
