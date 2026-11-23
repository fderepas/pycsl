#!/bin/bash
# chainB.sh : head sweep (h1 snapshot) + compares vs base, then witnesses (b0 and h1 pycsl, full proof),
# then the probes' full proofs on b0 and h1. One NORMAL job.
U=/home/fabrice/git/pycsl-u70/scratchpad/u70; G=$U/logs/G; B0=/home/fabrice/git/pycsl-u70-b0; H1=/home/fabrice/git/pycsl-u70-h1
bash $U/tools/S.sh $H1 $G/h1
cd $H1
python3 bin/byte-diff-compare.py $G/base/bd $G/h1/bd > $G/C1-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $G/C1-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/bd/pyref $G/h1/bd/pyref --min-files 2000 > $G/C1-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $G/C1-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/mir $G/h1/mir --min-files 45 > $G/C1-mir.txt 2>&1; echo "compare mirror rc=$? $(tail -2 $G/C1-mir.txt | tr '\n' ' ')"
diff -rq $G/base/mir $G/h1/mir > $G/D1-mir.txt 2>&1; echo "mirror diff -rq lines=$(wc -l < $G/D1-mir.txt)"
bash $U/tools/wit.sh p $H1 $U/logs/W-h1
bash $U/tools/wit.sh p $B0 $U/logs/W-b0
bash $U/tools/run.sh p $B0 $U/logs/P-b0
bash $U/tools/run.sh p $H1 $U/logs/P-h1
