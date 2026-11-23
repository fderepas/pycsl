#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u72/scratchpad/u72/tmp; mkdir -p $TMPDIR
# CMP.sh <base G dir> <head G dir> <outdir> : byte-diff-compare root / pyref / mirror + diff -rq mirror. cwd = u72 tree root.
B=$1; H=$2; O=$3; mkdir -p $O; cd /home/fabrice/git/pycsl-u72
python3 bin/byte-diff-compare.py $B/bd $H/bd > $O/C-root.txt 2>&1; echo "compare root rc=$? $(tail -2 $O/C-root.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $B/bd/pyref $H/bd/pyref --min-files 2000 > $O/C-pyref.txt 2>&1; echo "compare pyref rc=$? $(tail -2 $O/C-pyref.txt | tr '\n' ' ')"
python3 bin/byte-diff-compare.py $B/mir $H/mir --min-files 45 > $O/C-mir.txt 2>&1; echo "compare mirror rc=$? $(tail -2 $O/C-mir.txt | tr '\n' ' ')"
diff -rq $B/mir $H/mir > $O/D-mir.txt 2>&1; echo "diff -rq mirror lines=$(wc -l < $O/D-mir.txt)"
