#!/bin/bash
# prove-list.sh <worktree> <outdir> <file...> : whole-file pycsl proof of each file, sequentially; one verdict line per file
WT=$1; OUT=$2; shift 2; mkdir -p "$OUT"
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
for f in "$@"; do
  b=$(basename "$f" .py)
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  ( cd "$WT" && timeout 1200 "$WT/.venv/bin/python3" "$WT/src/pycsl/pycsl.py" $flags "$f" ) > "$OUT/$b.log" 2>&1
  rc=$?
  if grep -q "PIPELINE ERROR" "$OUT/$b.log"; then v=REFUSED; elif [ $rc -eq 0 ]; then v=PROVED; else v=FAIL; fi
  echo "$b rc=$rc $v"
done
