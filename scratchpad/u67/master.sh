#!/bin/bash
# master.sh : u67's ONE heavy job (sequential): base sweep (pycsl-u67b), proof battery (pycsl-u67), head gates (pycsl-u67h)
U=/home/fabrice/git/pycsl-u67/scratchpad/u67; S=$U/sw; mkdir -p $S/base $U/logs
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh; export PYTHON_CPU_COUNT=2
echo "master start $(date -u)"
cd /home/fabrice/git/pycsl-u67b && bin/byte-diff-sweep.sh $S/base/bd > $S/base/bd.log 2>&1; echo "base bd rc=$? $(tail -2 $S/base/bd.log | tr '\n' ' ')"
cd /home/fabrice/git/pycsl-u67b && bin/mirror-emit-sweep.sh $S/base/mir > $S/base/mir.log 2>&1; echo "base mir rc=$? $(tail -1 $S/base/mir.log)"
echo "base done $(date -u)" > $S/base/done.txt
bash $U/proofs.sh; echo "proofs done $(date -u)"; cat $U/pr/summary.txt
bash $U/tools/G.sh 2>&1
echo "master end $(date -u)"
