#!/bin/bash
# Emit all self-annotate mirrors and print md5 per file. $1 = repo root
set -u
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
R="$1"
cd "$R"
emit_one() {
  R="$1"; f="$2"
  PYTHONHASHSEED=0 timeout 600 python3 "$R/src/pycsl/pycsl.py" "$f" --import-path "$R/src/pycsl" --no-proof --no-typecheck --keep-mlw >/dev/null 2>&1
}
export -f emit_one
find "$R/src/self-annotate/src" -name '*.py' | sort > /tmp/_mirrors_$$.txt
xargs -P 8 -I{} bash -c 'emit_one "$@"' _ "$R" {} < /tmp/_mirrors_$$.txt
rm -f /tmp/_mirrors_$$.txt
find "$R/src/self-annotate/src" -name '*.mlw' | sort | while read m; do
  echo "$(md5sum "$m" | cut -d' ' -f1)  ${m#$R/}"
done
