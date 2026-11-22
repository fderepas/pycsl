#!/bin/bash
# full.sh <tree> <files...> : full proof verdict per file (default model), passing the file's own `# pycsl-flags:` header (run #7 fix)
T=$1; shift
cd $T
for f in "$@"; do
  fl=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  o=$(PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH PYTHONHASHSEED=0 timeout 600 .venv/bin/python3 src/pycsl/pycsl.py "$f" --import-path src/pycsl $fl 2>&1)
  c=$(printf '%s' "$o" | grep -oE "Verification SUCCESS|Verification FAILED|PYCSL-R[0-9]+[A-Z0-9-]*|PIPELINE ERROR" | sort | head -2 | tr "\n" " ")
  echo -e "$(basename $f)\t${c:-OTHER}"
done
