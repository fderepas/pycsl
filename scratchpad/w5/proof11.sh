#!/bin/bash
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/tmp
mkdir -p "$TMPDIR"
cd /home/fabrice/git/pycsl
for f in module6_whyml/stmt_control_flow; do
  n=$(echo $f | tr '/' '_')
  PYTHONHASHSEED=0 timeout 14400 python3 src/pycsl/pycsl.py src/self-annotate/src/$f.py --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' > scratchpad/w5/proofs/${n}_G.log 2>&1
  echo $? > scratchpad/w5/proofs/${n}_G.rc
done
echo DONE5 > scratchpad/w5/proofs/ALLDONE5
