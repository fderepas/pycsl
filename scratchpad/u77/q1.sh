#!/bin/bash
R=/home/fabrice/git/pycsl-u77/scratchpad/u77/run.sh
for t in h b; do
 for n in b1 b1r c15 c15n c15i c15l c15w; do $R $t $n --no-proof --soundness-report; done
 SFX=.strict $R $t b1 --no-proof --strict-float-finite
 SFX=.strict $R $t b1r --no-proof --strict-float-finite
done
echo QDONE
