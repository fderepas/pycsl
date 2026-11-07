#!/bin/bash
# sweep-chunk.sh <tree> <outdir> <budget_s> : resumable, chunked replica of bin/byte-diff-sweep.sh
# (same emit_one / emit_pyref commands, same naming, same SOURCES.txt manifests). Starts no new
# file after <budget_s> seconds; a file is marked done only after its emission returned.
# Prints REMAINING=<n> at the end. Run it AS a heavy.sh command.
set -u
T=$1; OUT=$2; B=$3
ROOT=$T; PY=$ROOT/.venv/bin/python3; JOBS=6
DL=$(( $(date +%s) + B ))
mkdir -p "$OUT/pyref" "$OUT/.done"
cd "$ROOT"
SRC=$(ls "$ROOT"/test-suite/corpus/pycsl-reference/*.py)
printf '%s\n' "$SRC" | xargs -n1 basename > "$OUT/SOURCES.txt"
PYREF_ROOT="$ROOT/test-suite/corpus/python-reference"
PSRC=$(find "$PYREF_ROOT" -name '*.py')
printf '%s\n' "$PSRC" | while IFS= read -r f; do
  rel="${f#$PYREF_ROOT/}"; printf 'pyref__%s.py\n' "$(printf '%s' "${rel%.py}" | tr '/' '_')"
done > "$OUT/pyref/SOURCES.txt"
one() {
  f="$1"; OUT="$2"; ROOT="$3"; PY="$4"; DL="$5"
  [ "$(date +%s)" -ge "$DL" ] && exit 0
  case "$f" in
    "$ROOT"/test-suite/corpus/python-reference/*)
      rel="${f#$ROOT/test-suite/corpus/python-reference/}"
      name="pyref__$(printf '%s' "${rel%.py}" | tr '/' '_')"
      [ -e "$OUT/.done/$name" ] && exit 0
      d=$(dirname "$f"); b=$(basename "$f" .py)
      flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
      rm -f "$d/$b.mlw"
      $PY "$ROOT/src/pycsl/pycsl.py" --no-proof --no-typecheck --keep-mlw $flags "$f" >/dev/null 2>&1
      [ -f "$d/$b.mlw" ] && mv "$d/$b.mlw" "$OUT/pyref/$name.mlw"
      touch "$OUT/.done/$name" ;;
    *)
      name=$(basename "$f" .py)
      [ -e "$OUT/.done/$name" ] && exit 0
      flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
      rm -f "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw"
      $PY "$ROOT/src/pycsl/pycsl.py" --no-proof --no-typecheck --keep-mlw $flags "$f" >/dev/null 2>&1
      [ -f "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw" ] && \
        mv "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw" "$OUT/$name.mlw"
      touch "$OUT/.done/$name" ;;
  esac
}
export -f one
{ printf '%s\n' "$SRC"; printf '%s\n' "$PSRC"; } | xargs -P "$JOBS" -I{} bash -c 'one "$@"' _ {} "$OUT" "$ROOT" "$PY" "$DL"
N=$(( $(wc -l < "$OUT/SOURCES.txt") + $(wc -l < "$OUT/pyref/SOURCES.txt") ))
D=$(ls "$OUT/.done" | wc -l)
echo "done=$D total=$N REMAINING=$(( N - D )) root_mlw=$(ls "$OUT"/*.mlw 2>/dev/null | wc -l) pyref_mlw=$(ls "$OUT"/pyref/*.mlw 2>/dev/null | wc -l)"
