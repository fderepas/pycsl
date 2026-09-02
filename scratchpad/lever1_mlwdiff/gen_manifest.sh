#!/bin/bash
# Emit each SUITE file's .mlw (fast, no typecheck) and md5 it -> manifest.
OUT="$1"
: > "$OUT"
while read -r f; do
  [ -z "$f" ] && continue
  PYTHONHASHSEED=0 timeout 300 python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl --no-typecheck --keep-mlw </dev/null >/dev/null 2>&1
  mlw="${f%.py}.mlw"
  if [ -f "$mlw" ]; then
    echo "$(md5sum "$mlw" | awk '{print $1}')  $mlw" >> "$OUT"
  else
    echo "MISSING  $mlw" >> "$OUT"
  fi
done < scratchpad/lever1_mlwdiff/filelist.txt
