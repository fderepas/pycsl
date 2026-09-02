#!/bin/bash
# Emit all mirror .mlw WITH L3-tc (lesson (ww)) and md5 them into a keyed manifest.
# Usage: sweep.sh <repo-root> <outdir>
set -u
ROOT="$1"; OUT="$2"
cd "$ROOT" || exit 1
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
mkdir -p "$OUT"
: > "$OUT/manifest.md5"
while read -r rel; do
    [ -z "$rel" ] && continue
    key=$(echo "$rel" | tr '/' '_')
    out=$(PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py "$rel" --import-path src/pycsl --no-proof --keep-mlw 2>&1)
    tc="TC_OK"
    echo "$out" | grep -q "L3-tc ✓" || tc="TC_FAIL"
    mlw="${rel%.py}.mlw"
    if [ -f "$mlw" ]; then
        md5=$(md5sum "$mlw" | awk '{print $1}')
        rm -f "$mlw"
    else
        md5="NO_MLW"
    fi
    echo "$md5  $tc  $rel" >> "$OUT/manifest.md5"
done < <(find src/self-annotate/src -name '*.py' | sort)
echo "DONE $(wc -l < "$OUT/manifest.md5") files; TC_FAIL=$(grep -c TC_FAIL "$OUT/manifest.md5")"
