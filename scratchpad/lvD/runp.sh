#!/bin/bash
# runp.sh <rel> <fn> <outdir> <subsfile> : survey with a patch, one QUICK heavy call
L=/home/fabrice/git/pycsl-lvD/scratchpad/lvD; o=$(realpath -m $3); s=$(realpath $4); mkdir -p $o
SUBS=$s PATCH=$L/sub.py /home/fabrice/git/pycsl/scratchpad/heavy/heavy.sh $L/survey.sh "$1" "$2" $o --no-proof < /dev/null
tail -1 $o/results.tsv | cut -f2-5 | cut -c1-400
