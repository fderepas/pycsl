#!/bin/bash
# planes-emit.sh <tree> <outdir> : the shared mirror emission of bin/run-soundness-planes.sh (same command,
# same single-underscore naming), run 6-parallel and resumable. Run AS a heavy.sh command.
PROJECT_ROOT=$1; OUT=$2; mkdir -p "$OUT/.done"
_py="$PROJECT_ROOT/.venv/bin/python3"
one() {
  PROJECT_ROOT=$1; OUT=$2; _py=$3; _src=$4
  _rel="${_src#"$PROJECT_ROOT/src/self-annotate/src/"}"; _name="${_rel%.py}"; _name="${_name//\//_}"
  [ -e "$OUT/.done/$_name" ] && exit 0
  rm -f "${_src%.py}.mlw"
  (cd "$PROJECT_ROOT" && PYTHONHASHSEED=0 "$_py" src/pycsl/pycsl.py "$_src" --import-path "$PROJECT_ROOT/src/pycsl" --no-proof --keep-mlw) >/dev/null 2>&1
  [ -f "${_src%.py}.mlw" ] && mv "${_src%.py}.mlw" "$OUT/$_name.mlw"
  touch "$OUT/.done/$_name"
}
export -f one
find "$PROJECT_ROOT/src/self-annotate/src" -name '*.py' | sort | xargs -P 6 -I{} bash -c 'one "$@"' _ "$PROJECT_ROOT" "$OUT" "$_py" {}
echo "emitted $(ls "$OUT"/*.mlw | wc -l) done $(ls "$OUT/.done" | wc -l)"
