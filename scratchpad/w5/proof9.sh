#!/bin/bash
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/tmp
mkdir -p "$TMPDIR"
cd /home/fabrice/git/pycsl
for f in module6_whyml/scc module6_whyml/auto_trust frontend/ir_resolve frontend/Module5_IREmitter pycsl; do
  n=$(echo $f | tr '/' '_')
  PYTHONHASHSEED=0 timeout 14400 python3 src/pycsl/pycsl.py src/self-annotate/src/$f.py --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' > scratchpad/w5/proofs/${n}_F.log 2>&1
  echo $? > scratchpad/w5/proofs/${n}_F.rc
done
echo DONE3 > scratchpad/w5/proofs/ALLDONE3
