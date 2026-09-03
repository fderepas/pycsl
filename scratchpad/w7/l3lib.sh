#!/bin/bash
T="$1"; cd "$T"
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
export TMPDIR=/home/fabrice/git/pycsl/scratchpad/w7/tmp
ok=0; bad=""
for f in $(find src/pycsl_lib -name '*.py' ! -name '*_demo.py' | sort); do
  r=$(PYTHONHASHSEED=0 timeout 300 python3 src/pycsl/pycsl.py "$f" --no-proof 2>&1 | grep -c "L3-tc ✓")
  if [ "$r" -ge 1 ]; then ok=$((ok+1)); else bad="$bad $f"; fi
done
echo "L3-tc GREEN: $ok"
echo "FAIL:$bad" | tr ' ' '\n'
