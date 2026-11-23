#!/bin/bash
# Q.sh <tree> <tag> : --no-proof (q) of every probe and the u73 witnesses/helpers with <tree>'s pycsl (QUICK job)
U=/home/fabrice/git/pycsl-u73/scratchpad/u73; L=$U/logs/Q-$2; mkdir -p $L; T=$1
echo "## $2 $T $(git -C $T rev-parse --short HEAD) $(date -u)"
bash $U/tools/D.sh q $T $L/d $(cat $U/tools/u73.lst $U/tools/rt81.lst) | sed 's/^/[d] /'
bash $U/tools/r.sh q $T $L/p $U/tools/u71all.lst | sed 's/^/[p] /'
bash $U/tools/wit.sh q $T $L/w | sed 's/^/[w] /'
echo "## end $(date -u)"
