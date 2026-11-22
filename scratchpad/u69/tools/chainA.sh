#!/bin/bash
# chainA.sh : base sweep (b1 = 0132f6e4d, my branch base) then head sweep (h1 snapshot), compares. One NORMAL job.
W=/home/fabrice/git/pycsl-u69; G=$W/scratchpad/u69/logs/G; mkdir -p $G
bash $W/scratchpad/u69/tools/S.sh /home/fabrice/git/pycsl-u69-b1 $G/base
bash $W/scratchpad/u69/tools/S.sh /home/fabrice/git/pycsl-u69-h1 $G/h1
cd $W
python3 bin/byte-diff-compare.py $G/base/bd $G/h1/bd > $G/C1-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $G/C1-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/bd/pyref $G/h1/bd/pyref --min-files 2000 > $G/C1-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $G/C1-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/mir $G/h1/mir --min-files 45 > $G/C1-mir.txt 2>&1; echo "compare mirror rc=$? $(tail -2 $G/C1-mir.txt | tr '\n' ' ')"
diff -rq $G/base/mir $G/h1/mir > $G/D1-mir.txt 2>&1; echo "mirror diff -rq lines=$(wc -l < $G/D1-mir.txt)"
