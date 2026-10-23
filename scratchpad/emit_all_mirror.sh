#!/bin/bash
# Emit all 52 mirror .mlw and md5 them into a keyed manifest.
# Usage: emit_all_mirror.sh <outdir>
set -u
cd /home/fabrice.derepas@canonical.com/git/pycsl
OUT="$1"
mkdir -p "$OUT"
: > "$OUT/manifest.md5"
while read -r rel; do
    [ -z "$rel" ] && continue
    key=$(echo "$rel" | tr '/' '_')
    PYTHONHASHSEED=0 python3 src/pycsl/pycsl.py "$rel" --import-path src/pycsl --no-proof --no-typecheck --keep-mlw >/dev/null 2>&1
    mlw="${rel%.py}.mlw"
    if [ -f "$mlw" ]; then
        md5=$(md5sum "$mlw" | awk '{print $1}')
        cp "$mlw" "$OUT/$key.mlw"
    else
        md5="NO_MLW"
    fi
    echo "$md5  $rel" >> "$OUT/manifest.md5"
done < <(find src/self-annotate/src -name '*.py' | sort)
echo "DONE $(wc -l < "$OUT/manifest.md5") files"
