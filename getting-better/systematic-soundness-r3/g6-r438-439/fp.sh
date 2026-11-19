#!/bin/bash
# fp.sh <tree> <files...> : FULL proof run of each file with <tree>'s pycsl (its pycsl-flags);
# one row: file, rc, verdict (Verification SUCCESS / FAIL / first refusal line). Run AS: heavy.sh fp.sh ...
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
T=$1; shift
for f in "$@"; do
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  o=$(cd "$(dirname "$f")" && PYTHONHASHSEED=0 timeout 600 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" $flags "$f" 2>&1); rc=$?
  c=$(printf '%s\n' "$o" | grep -A1 'PIPELINE ERROR' | sed -n 2p | tr '\t' ' ' | cut -c1-110)
  v=$(printf '%s\n' "$o" | grep -oE 'Verification (SUCCESS|FAIL[A-Z]*)' | head -1)
  printf '%s\t%s\t%s\n' "$(basename "$f")" "$rc" "${c:-${v:-$(printf '%s' "$o" | tail -1 | cut -c1-110)}}"
done
