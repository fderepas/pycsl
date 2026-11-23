#!/bin/bash
# chain2.sh : head sweep of snapshot h2 (b95cb8767) + compares vs base b0; J (b0 + h2) + b1 witnesses + census row
# re-check; then GATES on the u66 tree. One NORMAL job, sequential.
W=/home/fabrice/git/pycsl-u66; U=$W/scratchpad/u66; G=$U/logs/G
bash $U/tools/S.sh /home/fabrice/git/pycsl-u66-h2 $G/h2
cd $W
python3 bin/byte-diff-compare.py $G/base/bd $G/h2/bd > $G/C2-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $G/C2-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/bd/pyref $G/h2/bd/pyref --min-files 2000 > $G/C2-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $G/C2-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/mir $G/h2/mir --min-files 45 > $G/C2-mir.txt 2>&1; echo "compare mirror rc=$? $(tail -2 $G/C2-mir.txt | tr '\n' ' ')"
diff -rq $G/base/mir $G/h2/mir > $G/D2-mir.txt 2>&1; echo "mirror diff -rq lines=$(wc -l < $G/D2-mir.txt)"
bash $U/tools/J.sh /home/fabrice/git/pycsl-u66-h2 h2 2>&1 | sed 's/^/[J] /'
bash $U/tools/wit.sh p /home/fabrice/git/pycsl-u66-b1 $U/logs/J-h2/w-b1 2>&1 | sed 's/^/[Jb1] /'
bash $U/tools/run.sh q /home/fabrice/git/pycsl-u66-h2 $U/logs/q-h2 2>&1 | sed 's/^/[qh2] /'
bash $U/tools/CR.sh > $U/logs/CR-row2.tsv 2>$U/logs/CR-row2.err; echo "CR rc=$? cmp-committed: $(grep '^10380_' bin/refusal-witness-census.tsv | cmp - $U/logs/CR-row2.tsv && echo IDENTICAL)"
bash $U/tools/GATES.sh $U/logs/GATES 2>&1
