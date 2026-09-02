#!/bin/bash
OUT="$1"; mkdir -p "$OUT"; PY=".venv/bin/python3"
while read -r f; do
  [ -z "$f" ] && continue
  d=$(dirname "$f"); name=$(basename "$f" .py); mlw="$d/$name.mlw"
  rm -f "$mlw"
  $PY src/pycsl/pycsl.py --no-proof --no-typecheck --keep-mlw "$f" --import-path src/pycsl >/dev/null 2>&1
  if [ -f "$mlw" ]; then
    cp "$mlw" "$OUT/${name}.mlw"; echo "$(md5sum "$mlw" | cut -d' ' -f1)  $f"; rm -f "$mlw"
  else echo "NOEMIT  $f"; fi
done < scratchpad/nt/mirror_files.txt
