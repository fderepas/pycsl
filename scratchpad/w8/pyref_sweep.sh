#!/usr/bin/env bash
# Emission sweep over the python-reference corpus (byte-diff-sweep.sh only covers
# pycsl-reference). Usage: pyref_sweep.sh <repo-root> <out-dir>
set -u
ROOT="$1"; OUT="$2"; PY="$ROOT/.venv/bin/python3"
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
mkdir -p "$OUT"; : > "$OUT/refused.txt"
emit_one() {
  f="$1"; OUT="$2"; ROOT="$3"; PY="$4"
  rel="${f#$ROOT/test-suite/corpus/python-reference/}"
  key=$(echo "$rel" | tr '/' '_'); key="${key%.py}"
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  mlw="${f%.py}.mlw"
  rm -f "$mlw"
  out=$($PY "$ROOT/src/pycsl/pycsl.py" --no-proof --no-typecheck --keep-mlw $flags "$f" 2>&1)
  if [ -f "$mlw" ]; then mv "$mlw" "$OUT/$key.mlw"; else echo "$rel" >> "$OUT/refused.txt"; fi
}
export -f emit_one
find "$ROOT/test-suite/corpus/python-reference" -name '*.py' | sort | \
  xargs -P 4 -I{} bash -c 'emit_one "$@"' _ {} "$OUT" "$ROOT" "$PY"
echo "emitted $(ls "$OUT"/*.mlw 2>/dev/null | wc -l) ; no-mlw $(wc -l < "$OUT/refused.txt")"
