#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
OUT="$1"; : > "$OUT"
find src/self-annotate/src -name '*.py' | sort | while read -r f; do
  r=$(PYTHONHASHSEED=0 timeout 900 python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl --no-proof 2>&1 | grep -c 'L3-tc ✓')
  echo -e "$r\t$f" >> "$OUT"
done
echo DONE >> "$OUT"
