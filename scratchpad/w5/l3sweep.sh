#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
OUT="$1"; mkdir -p "$OUT"; ok=0; fail=""
for f in $(find src/self-annotate/src -name '*.py' | sort); do
  n=$(echo ${f#src/self-annotate/src/} | tr '/' '_' | sed 's/.py$/.mlw/')
  r=$(PYTHONHASHSEED=0 timeout 600 python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl --no-proof --keep-mlw 2>&1 | grep -c "L3-tc ✓")
  m="${f%.py}.mlw"
  if [ "$r" -ge 1 ]; then ok=$((ok+1)); else fail="$fail ${f#src/self-annotate/src/}"; fi
  [ -f "$m" ] && mv "$m" "$OUT/$n"
done
echo "L3-tc GREEN: $ok / 52"
echo "FAIL:$fail"
