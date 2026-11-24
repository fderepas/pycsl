#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u75/scratchpad/u75/tmp; mkdir -p "$TMPDIR"
# chain3.sh : (one job) census rows (real _census_row) for 10490-10495 appended; witness/helper full proofs on the
# final worktree; GATES (fidelity + ledger planes, fast planes teed, rwc, ce, foc, cdm, cvd) on the u75 worktree
U=/home/fabrice/git/pycsl-u75/scratchpad/u75; W=/home/fabrice/git/pycsl-u75
echo "chain3 start $(date -u) $(git -C $W rev-parse --short HEAD)"
bash $U/tools/CR.sh > $U/logs/CR-rows.tsv 2>$U/logs/CR-rows.err; echo "CR rc=$? rows=$(wc -l < $U/logs/CR-rows.tsv)"
cd $W; if [ "$(wc -l < $U/logs/CR-rows.tsv)" = 6 ] && ! grep -q '^10490_' bin/refusal-witness-census.tsv; then cat $U/logs/CR-rows.tsv >> bin/refusal-witness-census.tsv; echo "census rows appended"; fi
cd $W && python3 bin/byte-diff-compare.py $U/logs/G/b1/bd $U/logs/G/h2/bd --expect-gone 6026_gen37_r409_ctl_stdlib_obj > $U/logs/G/C-h2-root-declared.txt 2>&1; echo "compare root (declared GONE 6026) rc=$? $(tail -2 $U/logs/G/C-h2-root-declared.txt | tr "\n" " ")"
bash $U/tools/wit.sh p $W $U/logs/W-final | sed 's/^/[W] /'
bash $U/tools/GATES.sh $U/logs/GATES 2>&1
echo "chain3 end $(date -u)"
