#!/bin/bash
# J.sh <headtree> <tag> : full proofs of the key probes + u66 probes and the u66 witnesses, base b0 and <headtree>
U=/home/fabrice/git/pycsl-u66/scratchpad/u66; L=$U/logs/J-$2; mkdir -p $L
for t in /home/fabrice/git/pycsl-u66-b0:b0 $1:head; do T=${t%%:*}; n=${t##*:}
  echo "## $n $T $(git -C $T rev-parse --short HEAD)"
  bash $U/tools/run.sh q $T $L/q-$n $U/tools/probes-u66.lst
  bash $U/tools/run.sh p $T $L/p-$n $U/tools/probes-p.lst
  bash $U/tools/run.sh p $T $L/pu-$n $U/tools/probes-u66.lst
  bash $U/tools/wit.sh p $T $L/w-$n
done
