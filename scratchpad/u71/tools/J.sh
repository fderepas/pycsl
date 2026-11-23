#!/bin/bash
# J.sh <tree> <tag> [list] : full proof (p) of every probe of the list (default all.lst) + the u71 witnesses/helpers,
# all with <tree>'s pycsl. One NORMAL job.
U=/home/fabrice/git/pycsl-u71/scratchpad/u71; L=$U/logs/J-$2; mkdir -p $L; T=$1
echo "## $2 $T $(git -C $T rev-parse --short HEAD) $(date -u)"
bash $U/tools/r.sh p $T $L/p ${3:-$U/tools/all.lst} | sed 's/^/[p] /'
bash $U/tools/wit.sh p $T $L/w | sed 's/^/[w] /'
echo "## end $(date -u)"
