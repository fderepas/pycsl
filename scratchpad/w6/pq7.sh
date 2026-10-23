#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
wait_slot() {
  while [ "$(pgrep -f 'pycsl.py src/self-annotate' | wc -l)" -ge 2 ]; do sleep 60; done
}
for f in frontend/ir_resolve frontend/__init__; do
  n=$(echo $f | tr '/' '_')
  wait_slot
  PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py "src/self-annotate/src/$f.py" \
    --import-path src/pycsl --provers 'Alt-Ergo,2.6.3,,Z3,4.13.3,' \
    > scratchpad/w6/proofs/${n}_dg33.log 2>&1
  echo "rc=$? ${n}_dg33" >> scratchpad/w6/proofs/RC.txt
done
