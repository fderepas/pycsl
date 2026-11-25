#!/bin/bash
# q.sh <names>: QUICK --no-proof emissions at head and base
for n in "$@"; do for t in h b; do /home/fabrice/git/pycsl-u76/scratchpad/u76/run.sh $t $n --no-proof; done; done
