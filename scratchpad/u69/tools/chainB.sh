#!/bin/bash
# chainB.sh : head sweep of snapshot h2 (final src) + compares vs base b1; J (probes q + p, witnesses p) on h2, b1, b0;
# census rows 10405 / 10406 (real _census_row, u69 tree). One NORMAL job, sequential.
W=/home/fabrice/git/pycsl-u69; U=$W/scratchpad/u69; G=$U/logs/G
bash $U/tools/S.sh /home/fabrice/git/pycsl-u69-h2 $G/h2
cd $W
python3 bin/byte-diff-compare.py $G/base/bd $G/h2/bd > $G/C2-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $G/C2-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/bd/pyref $G/h2/bd/pyref --min-files 2000 > $G/C2-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $G/C2-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/mir $G/h2/mir --min-files 45 > $G/C2-mir.txt 2>&1; echo "compare mirror rc=$? $(tail -2 $G/C2-mir.txt | tr '\n' ' ')"
diff -rq $G/base/mir $G/h2/mir > $G/D2-mir.txt 2>&1; echo "mirror diff -rq lines=$(wc -l < $G/D2-mir.txt)"
for t in /home/fabrice/git/pycsl-u69-h2:h2 /home/fabrice/git/pycsl-u69-b1:b1 /home/fabrice/git/pycsl-u69-b0:b0; do
  bash $U/tools/J.sh ${t%%:*} ${t##*:} 2>&1 | sed "s/^/[J ${t##*:}] /"
done
bash $U/tools/CR.sh > $U/logs/CR-rows.tsv 2>$U/logs/CR-rows.err; echo "CR rc=$? $(cut -c1-160 $U/logs/CR-rows.tsv)"
