#!/usr/bin/env bash
# scan.sh <list> <tag> <budget-seconds> <jobs> --no-proof
# Resumable LOG-MODE scan for spike S1: runs the patched tree's pycsl.py (--no-proof --no-typecheck)
# on every file of <list> not yet in <tag>.done, logging R-gate rows to <tag>.log and the rc to
# <tag>.rc. Stops launching new files after <budget-seconds>.
set -u
S=/tmp/claude-1000/-home-fabrice-git-pycsl/0119d6ca-595a-4b95-ab54-21d812c2f0f2/scratchpad/rg
T=$S/tree
LIST="$1"; TAG="$2"; BUDGET="$3"; JOBS="$4"
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
export PYCSL_RG_LOG=$S/spike/$TAG.log
touch "$S/spike/$TAG.done"
one() {
  f="$1"; TAG="$2"; S="$3"; T="$4"
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  case "$f" in
    */self-annotate/src/*) extra="--import-path $T/src/pycsl" ;;
    *) extra="" ;;
  esac
  d=$(dirname "$f"); b=$(basename "$f" .py)
  PYTHONHASHSEED=0 timeout 600 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --no-proof --no-typecheck $extra $flags "$f" > "$S/spike/out/$TAG.$(echo "$f" | md5sum | cut -c1-12).out" 2>&1
  rc=$?
  rm -f "$d/$b.mlw"
  printf '%s\t%s\n' "$f" "$rc" >> "$S/spike/$TAG.rc"
  printf '%s\n' "$f" >> "$S/spike/$TAG.done"
}
export -f one
mkdir -p $S/spike/out
start=$(date +%s)
todo=$(grep -vxFf "$S/spike/$TAG.done" "$LIST")
n=0
while IFS= read -r f; do
  [ -z "$f" ] && continue
  now=$(date +%s)
  [ $((now - start)) -ge "$BUDGET" ] && break
  while [ "$(jobs -rp | wc -l)" -ge "$JOBS" ]; do sleep 0.3; done
  one "$f" "$TAG" "$S" "$T" &
  n=$((n+1))
done <<< "$todo"
wait
echo "launched $n; done $(wc -l < $S/spike/$TAG.done) / $(wc -l < $LIST)"
