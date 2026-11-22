#!/bin/bash
# int75 (L18 candidate): driver whole-file proofs of the mirror movers under final tooling, sequential, PRIO
cd /home/fabrice/git/pycsl
PQ_ENV="HEAVY_PRIO=1 PYTHON_CPU_COUNT=2" bash scratchpad/run9/bin/proveq.sh /home/fabrice/git/pycsl-int75 int75 pycsl.py proof2why3/normalize.py frontend/Module3_Weaver.py
echo PROOFS-DONE >> scratchpad/run9/int75-proofs.txt
