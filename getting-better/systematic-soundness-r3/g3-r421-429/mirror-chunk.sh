#!/bin/bash
# mirror-chunk.sh <tree> <outdir> <budget_s> : resumable replica of bin/mirror-emit-sweep.sh (same
# emit command, same key, same SOURCES.txt). Starts no new file after <budget_s>. Run AS a heavy.sh cmd.
set -u
ROOT=$1; OUT=$2; B=$3; PY="$ROOT/.venv/bin/python3"; JOBS=6
DL=$(( $(date +%s) + B ))
mkdir -p "$OUT/.done"
SRC=$(find "$ROOT/src/self-annotate/src" -name '*.py' | sort)
printf '%s\n' "$SRC" | sed "s#^$ROOT/src/self-annotate/src/##; s/\.py$//; s#/#__#g; s/$/.mlw/" | sort > "$OUT/SOURCES.txt"
one() {
  f="$1"; OUT="$2"; ROOT="$3"; PY="$4"; DL="$5"
  [ "$(date +%s)" -ge "$DL" ] && exit 0
  name=$(printf '%s' "${f#"$ROOT/src/self-annotate/src/"}" | sed 's/\.py$//; s#/#__#g')
  [ -e "$OUT/.done/$name" ] && exit 0
  if git -C "$ROOT" ls-files --error-unmatch "${f%.py}.mlw" >/dev/null 2>&1; then echo "TRACKED ${f%.py}.mlw" >&2; exit 0; fi
  rm -f "${f%.py}.mlw"
  s=$(date +%s)
  PYTHONHASHSEED=0 timeout 900 "$PY" "$ROOT/src/pycsl/pycsl.py" --no-proof --no-typecheck --keep-mlw --import-path "$ROOT/src/pycsl" "$f" >/dev/null 2>&1
  [ -f "${f%.py}.mlw" ] && mv "${f%.py}.mlw" "$OUT/$name.mlw"
  echo "$name $(( $(date +%s) - s ))s" >> "$OUT/times.txt"
  touch "$OUT/.done/$name"
}
export -f one
printf '%s\n' "$SRC" | xargs -P "$JOBS" -I {} bash -c 'one "$@"' _ {} "$OUT" "$ROOT" "$PY" "$DL"
echo "done=$(ls "$OUT/.done" | wc -l) of $(printf '%s\n' "$SRC" | wc -l) mlw=$(ls "$OUT"/*.mlw 2>/dev/null | wc -l)"
