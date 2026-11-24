#!/bin/bash
# chainC.sh : census rows 10405 / 10406 (real _census_row) appended to bin/refusal-witness-census.tsv; head sweep of
# snapshot h3 (final src 73f47db9d) + compares vs base b1; J on h3; GATES on the u69 tree. One NORMAL job, sequential.
W=/home/fabrice/git/pycsl-u69; U=$W/scratchpad/u69; G=$U/logs/G
bash $U/tools/CR.sh > $U/logs/CR-rows3.tsv 2>$U/logs/CR-rows3.err; echo "CR rc=$? rows=$(wc -l < $U/logs/CR-rows3.tsv)"
cd $W; if [ "$(wc -l < $U/logs/CR-rows3.tsv)" = 2 ] && ! grep -q '^10405_' bin/refusal-witness-census.tsv; then cat $U/logs/CR-rows3.tsv >> bin/refusal-witness-census.tsv; echo "census rows appended"; fi
bash $U/tools/S.sh /home/fabrice/git/pycsl-u69-h3 $G/h3
cd $W
python3 bin/byte-diff-compare.py $G/base/bd $G/h3/bd > $G/C3-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $G/C3-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/bd/pyref $G/h3/bd/pyref --min-files 2000 > $G/C3-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $G/C3-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/mir $G/h3/mir --min-files 45 > $G/C3-mir.txt 2>&1; echo "compare mirror rc=$? $(tail -2 $G/C3-mir.txt | tr '\n' ' ')"
diff -rq $G/base/mir $G/h3/mir > $G/D3-mir.txt 2>&1; echo "mirror diff -rq lines=$(wc -l < $G/D3-mir.txt)"
bash $U/tools/J.sh /home/fabrice/git/pycsl-u69-h3 h3 2>&1 | sed "s/^/[J h3] /"
bash $U/tools/GATES.sh $U/logs/GATES 2>&1
