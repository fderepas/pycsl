#!/bin/bash
R=/home/fabrice/git/pycsl-u77/scratchpad/u77/run.sh
for t in h b; do for n in c15 c15n c15i c15l c15w b1 b1r; do SFX=.np $R $t $n --no-proof; done; done
echo QDONE
