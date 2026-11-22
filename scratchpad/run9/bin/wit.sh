#!/bin/bash
# wit.sh <tree> <mm> <files...> : front-end verdict per file (--no-proof)
T=$1; MM=$2; shift 2
cd $T
for f in "$@"; do
  o=$(PYTHONHASHSEED=0 timeout 300 .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl --no-proof --memory-model $MM 2>&1)
  c=$(printf '%s' "$o" | grep -oE "PYCSL-R[0-9]+[A-Z0-9-]*" | head -1)
  [ -z "$c" ] && c=$(printf '%s' "$o" | grep -qiE "PIPELINE ERROR|error" && echo "ERR:$(printf '%s' "$o" | grep -m1 -iE 'error' | cut -c1-100)" || echo "EMITTED")
  echo -e "$MM\t$(basename $f)\t$c"
done
