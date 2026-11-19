#!/usr/bin/env bash
# Emit every self-annotate mirror .mlw into $2, using the tree rooted at $1.
set -u
ROOT="$1"; OUT="$2"; mkdir -p "$OUT"
PY="$ROOT/.venv/bin/python3"; [ -x "$PY" ] || PY=python3
export PATH="$HOME/.opam/framac-coq8/bin:$PATH"
emit_one() {
  f="$1"; OUT="$2"; ROOT="$3"; PY="$4"
  rel="${f#$ROOT/src/self-annotate/src/}"; name="${rel//\//__}"; name="${name%.py}"
  rm -f "${f%.py}.mlw"
  PYTHONHASHSEED=0 $PY "$ROOT/src/pycsl/pycsl.py" --no-proof --no-typecheck --keep-mlw \
      --import-path "$ROOT/src/pycsl" "$f" >"$OUT/$name.log" 2>&1
  if [ -f "${f%.py}.mlw" ]; then mv "${f%.py}.mlw" "$OUT/$name.mlw"; fi
}
export -f emit_one
FILES=$(find "$ROOT/src/self-annotate/src" -name '*.py' | sort)
printf '%s\n' "$FILES" | xargs -P 6 -I{} bash -c 'emit_one "$@"' _ {} "$OUT" "$ROOT" "$PY"
echo "emitted $(ls "$OUT"/*.mlw 2>/dev/null | wc -l) of $(printf '%s\n' "$FILES" | wc -l)"
