#!/bin/bash
export TMPDIR=/home/fabrice/git/pycsl-u75/scratchpad/u75/tmp; mkdir -p "$TMPDIR"
# Q.sh <tree> <tag> [lists...] : --no-proof (q) of every probe list with <tree>'s pycsl (QUICK job)
U=/home/fabrice/git/pycsl-u75/scratchpad/u75; L=$U/logs/Q-$2; mkdir -p $L; T=$1; shift 2
LS="${@:-rt83 rt81 u73 u75}"
echo "## $T $(git -C $T rev-parse --short HEAD) $(date -u)"
for l in $LS; do [ -f $U/tools/$l.lst ] && bash $U/tools/D.sh q $T $L/d $(cat $U/tools/$l.lst) | sed "s/^/[$l] /"; done
[ -z "$*" ] && bash $U/tools/r.sh q $T $L/p $U/tools/u71all.lst | sed 's/^/[p] /'
echo "## end $(date -u)"
