#!/usr/bin/env bash
# sweep-part.sh <tree-root> <out> <part> <nparts> : same emission/naming as bin/byte-diff-sweep.sh,
# only files with (index % nparts == part). part=manifest writes the SOURCES.txt files only.
set -u
ROOT="$1"; OUT="$2"; PART="$3"; NP="$4"; PY="$ROOT/.venv/bin/python3"
mkdir -p "$OUT/pyref"
SRC=$(ls "$ROOT"/test-suite/corpus/pycsl-reference/*.py)
PYREF_ROOT="$ROOT/test-suite/corpus/python-reference"
PSRC=$(find "$PYREF_ROOT" -name '*.py')
if [ "$PART" = manifest ]; then
  printf '%s\n' "$SRC" | xargs -n1 basename > "$OUT/SOURCES.txt"
  printf '%s\n' "$PSRC" | while IFS= read -r f; do
    rel="${f#$PYREF_ROOT/}"; printf 'pyref__%s.py\n' "$(printf '%s' "${rel%.py}" | tr '/' '_')"
  done > "$OUT/pyref/SOURCES.txt"
  echo "manifest: $(wc -l < $OUT/SOURCES.txt) root, $(wc -l < $OUT/pyref/SOURCES.txt) pyref"; exit 0
fi
emit_one() {
  f="$1"; OUT="$2"; ROOT="$3"; PY="$4"; name=$(basename "$f" .py)
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  rm -f "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw"
  $PY "$ROOT/src/pycsl/pycsl.py" --no-proof --no-typecheck --keep-mlw $flags "$f" >/dev/null 2>&1
  [ -f "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw" ] && \
    mv "$ROOT/test-suite/corpus/pycsl-reference/$name.mlw" "$OUT/$name.mlw"
}
emit_pyref() {
  f="$1"; POUT="$2"; ROOT="$3"; PY="$4"
  rel="${f#$ROOT/test-suite/corpus/python-reference/}"
  name="pyref__$(printf '%s' "${rel%.py}" | tr '/' '_')"
  d=$(dirname "$f"); b=$(basename "$f" .py)
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  rm -f "$d/$b.mlw"
  $PY "$ROOT/src/pycsl/pycsl.py" --no-proof --no-typecheck --keep-mlw $flags "$f" >/dev/null 2>&1
  [ -f "$d/$b.mlw" ] && mv "$d/$b.mlw" "$POUT/$name.mlw"
}
export -f emit_one emit_pyref
printf '%s\n' "$SRC" | awk -v p="$PART" -v n="$NP" 'NR%n==p' | xargs -P 6 -I{} bash -c 'emit_one "$@"' _ {} "$OUT" "$ROOT" "$PY"
printf '%s\n' "$PSRC" | awk -v p="$PART" -v n="$NP" 'NR%n==p' | xargs -P 6 -I{} bash -c 'emit_pyref "$@"' _ {} "$OUT/pyref" "$ROOT" "$PY"
echo "part $PART/$NP done: $(ls $OUT/*.mlw | wc -l) root, $(ls $OUT/pyref/*.mlw | wc -l) pyref so far"
