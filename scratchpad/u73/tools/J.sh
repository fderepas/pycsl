#!/bin/bash
# J.sh <tree> <tag> : full proofs (p) of every probe (u71 list via r.sh, rt81 + u73 dirs via D.sh) and the u73
# witnesses/helpers, with <tree>'s pycsl. One NORMAL job.
U=/home/fabrice/git/pycsl-u73/scratchpad/u73; L=$U/logs/J-$2; mkdir -p $L; T=$1
echo "## $2 $T $(git -C $T rev-parse --short HEAD) $(date -u)"
bash $U/tools/D.sh p $T $L/d $(cat $U/tools/u73.lst $U/tools/rt81.lst) | sed 's/^/[d] /'
bash $U/tools/r.sh p $T $L/p $U/tools/u71all.lst | sed 's/^/[p] /'
bash $U/tools/wit.sh p $T $L/w | sed 's/^/[w] /'
echo "## end $(date -u)"
