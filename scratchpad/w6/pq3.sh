#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
for f in frontend/pure_ast frontend/desugar; do
  n=$(echo $f | tr '/' '_')
  PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py "src/self-annotate/src/$f.py" \
    --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' \
    > scratchpad/w6/proofs/$n.log 2>&1
  echo "rc=$? $n" >> scratchpad/w6/proofs/RC.txt
done
