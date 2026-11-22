#!/bin/bash
# chain1.sh : (after the base sweep) head sweep of the snapshot tree u66-h1, then compares. One NORMAL job.
W=/home/fabrice/git/pycsl-u66; G=$W/scratchpad/u66/logs/G
bash $W/scratchpad/u66/tools/S.sh /home/fabrice/git/pycsl-u66-h1 $G/h1
cd $W
python3 bin/byte-diff-compare.py $G/base/bd $G/h1/bd > $G/C1-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $G/C1-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/bd/pyref $G/h1/bd/pyref --min-files 2000 > $G/C1-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $G/C1-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/mir $G/h1/mir --min-files 45 > $G/C1-mir.txt 2>&1; echo "compare mirror rc=$? $(tail -2 $G/C1-mir.txt | tr '\n' ' ')"
diff -rq $G/base/mir $G/h1/mir > $G/D1-mir.txt 2>&1; echo "mirror diff -rq lines=$(wc -l < $G/D1-mir.txt)"
