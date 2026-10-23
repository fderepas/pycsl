#!/usr/bin/env bash
# Emit every mirror .py in ROOT to OUT/<key>.mlw
set -u
ROOT="$1"; OUT="$2"
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
mkdir -p "$OUT"; : > "$OUT/refused.txt"
cd "$ROOT"
find src/self-annotate/src -name '*.py' | sort | while read -r f; do
  key=$(echo "${f#src/self-annotate/src/}" | tr '/' '_'); key="${key%.py}"
  mlw="${f%.py}.mlw"; rm -f "$mlw"
  PYTHONHASHSEED=0 timeout 600 python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl \
      --no-proof --no-typecheck --keep-mlw >/dev/null 2>&1
  if [ -f "$mlw" ]; then mv "$mlw" "$OUT/$key.mlw"; else echo "$key" >> "$OUT/refused.txt"; fi
done
