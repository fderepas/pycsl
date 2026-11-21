#!/bin/bash
# np.sh <tree> <files...> : --no-proof run of each file from <tree>; one row: file, rc, first PYCSL code / SUCCESS.
# Run AS: heavy.sh np.sh --no-proof <tree> <files...> (the token makes it QUICK).
export PATH=$HOME/.opam/framac-coq8/bin:$PATH
[ "$1" = --no-proof ] && shift  # token only: heavy.sh classes the job QUICK
T=$1; shift
for f in "$@"; do
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  o=$(cd "$(dirname "$f")" && PYTHONHASHSEED=0 timeout 300 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --no-proof $flags "$f" 2>&1); rc=$?
  c=$(printf '%s\n' "$o" | grep -A1 'PIPELINE ERROR' | sed -n 2p | tr '\t' ' ' | cut -c1-140)
  printf '%s\t%s\t%s\n' "$(basename "$f")" "$rc" "${c:-$(printf '%s' "$o" | grep -oE 'Verification SUCCESS|No verification' | head -1)}"
done
