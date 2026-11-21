#!/bin/bash
# qcheck.sh <tag> <tree> : QUICK (--no-proof) diagnostic set: the 15 mirror units R614-v1 refused, the 46 corpus
# units it refused, the 169 red-team probes, the lvZ2 witnesses. Sequential; cwd = tree root.
tag=$1; T=$2; B=/home/fabrice/git/pycsl-lvZ2/scratchpad/lvZ2; L=$B/logs
$B/bin/miremit.sh $T $L/mir-$tag $(cat $L/mirgone.txt) > $L/mir-$tag.txt 2>&1
$B/bin/emit.sh gone-$tag $T $(sed "s#/home/fabrice/git/pycsl-lvZ2r/#$T/#" $L/gone-list.txt) > $L/emit-gone-$tag.tsv 2>&1
$B/bin/emit.sh pr-$tag $T $(cat $B/plist.txt) > $L/emit-pr-$tag.tsv 2>&1
$B/bin/emit.sh wit-$tag $T $(ls $T/test-suite/corpus/pycsl-reference/1028[0-9]_lvz2_*.py $T/test-suite/corpus/pycsl-reference/1029[0-6]_lvz2_*.py 2>/dev/null) > $L/emit-wit-$tag.tsv 2>&1
echo "QCHECK-DONE $(date -u +%FT%TZ)" >> $L/mir-$tag.txt
