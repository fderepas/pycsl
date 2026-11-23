#!/bin/bash
# CMP.sh <tag> : compare sweep G/<tag> against base G/base (root, pyref, mirror + diff -rq), cwd = u71 tree root
W=/home/fabrice/git/pycsl-u73; G=$W/scratchpad/u73/logs/G; t=$1; cd $W
python3 bin/byte-diff-compare.py $G/base/bd $G/$t/bd > $G/C-$t-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $G/C-$t-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/bd/pyref $G/$t/bd/pyref --min-files 2000 > $G/C-$t-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $G/C-$t-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $G/base/mir $G/$t/mir --min-files 45 > $G/C-$t-mir.txt 2>&1; echo "compare mirror rc=$? $(tail -2 $G/C-$t-mir.txt | tr '\n' ' ')"
diff -rq $G/base/mir $G/$t/mir > $G/D-$t-mir.txt 2>&1; echo "mirror diff -rq lines=$(wc -l < $G/D-$t-mir.txt)"
