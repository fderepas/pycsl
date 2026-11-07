#!/bin/bash
# mirror-run.sh <worktree> <outdir> <mode: tc|prove> <relpath-under-src/self-annotate/src>... : sequential
WT=$1; OUT=$2; MODE=$3; shift 3; mkdir -p "$OUT"
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
for r in "$@"; do
  f="$WT/src/self-annotate/src/$r"; b=$(printf '%s' "${r%.py}" | sed 's#/#__#g')
  extra=""; [ "$MODE" = tc ] && extra="--no-proof"
  start=$(date +%s)
  ( cd "$WT" && PYTHONHASHSEED=0 "$WT/.venv/bin/python3" "$WT/src/pycsl/pycsl.py" $extra --import-path "$WT/src/pycsl" "$f" ) > "$OUT/$b.$MODE.log" 2>&1
  rc=$?
  nv=$(grep -c "Prover result is: Valid" "$OUT/$b.$MODE.log")
  nn=$(grep "Prover result is:" "$OUT/$b.$MODE.log" | grep -vc "Valid")
  echo "$b mode=$MODE rc=$rc valid_lines=$nv nonvalid_lines=$nn secs=$(( $(date +%s) - start ))"
done
