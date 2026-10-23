#!/usr/bin/env bash
# gen #33: the seam BEFORE/AFTER measurement, ONE instrument, both passes.
# FOREGROUND ONLY — this ports a live body into the mirror and restores it in a `finally`,
# so it must never outlive its owner (the ownerless-writer rule).
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
export PYTHONHASHSEED=0
cd /home/fabrice/git/pycsl || exit 9
S="$1"; LABEL="$2"
OUT="$S/seam_${LABEL}.txt"
: > "$OUT"
echo "SEAMPROBE $LABEL START $(date -u +%FT%TZ) at $(git log --oneline -1)" | tee -a "$OUT"
while IFS=$'\t' read -r path names; do
    [ -z "$path" ] && continue
    case "$path" in \#*) continue;; esac
    echo "### $path" >> "$OUT"
    # shellcheck disable=SC2086
    timeout 1800 python3 bin/probe-conversion-candidates.py "$path" $names >> "$OUT" 2>&1
    echo "   (rc=$?)" >> "$OUT"
done < "$S/seam_targets.txt"
echo "SEAMPROBE $LABEL END $(date -u +%FT%TZ)" | tee -a "$OUT"
# The tree MUST be clean afterwards; assert it rather than hope.
echo "DIRTY_SRC=$(git status --porcelain -- src/ | wc -l)  STRAY_BAK=$(find src/self-annotate -name '*.py.bak' | wc -l)" | tee -a "$OUT"
