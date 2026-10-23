#!/bin/bash
set -u
ROOT="$1"; OUT="$2"
cd "$ROOT" || exit 1
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
mkdir -p "$OUT"
while read -r rel; do
    [ -z "$rel" ] && continue
    key=$(echo "$rel" | tr '/' '_')
    PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py "$rel" --import-path src/pycsl --no-proof --keep-mlw >/dev/null 2>&1
    mlw="${rel%.py}.mlw"
    [ -f "$mlw" ] && mv "$mlw" "$OUT/$key.mlw"
done < <(find src/self-annotate/src -name '*.py' | sort)
echo "kept $(ls "$OUT" | wc -l)"
