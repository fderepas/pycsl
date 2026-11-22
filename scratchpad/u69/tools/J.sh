#!/bin/bash
# J.sh <tree> <tag> : --no-proof of every probe (old rt76/u64/u66 + rt78 + u69), full proofs of the key probes,
# full proofs of the u69 witnesses + helpers, all with <tree>'s pycsl. One NORMAL job.
U=/home/fabrice/git/pycsl-u69/scratchpad/u69; L=$U/logs/J-$2; mkdir -p $L; T=$1
echo "## $2 $T $(git -C $T rev-parse --short HEAD) $(date -u)"
bash $U/tools/run.sh q $T $L/q-old $U/tools/old.lst | sed 's/^/[q-old] /'
bash $U/tools/run.sh q $T $L/q-new $U/tools/new.lst | sed 's/^/[q-new] /'
bash $U/tools/run.sh p $T $L/p-new $U/tools/P-new.lst | sed 's/^/[p-new] /'
bash $U/tools/run.sh p $T $L/p-old $U/tools/P-old.lst | sed 's/^/[p-old] /'
bash $U/tools/wit.sh p $T $L/w | sed 's/^/[w] /'
echo "## end $(date -u)"
