#!/bin/bash
# quick.sh <tree> <out> <file.py>... : --no-proof --no-typecheck emission of each file, cwd = tree
# root; prints the refusal code / message head or EMITTED. Honours `# pycsl-flags:`.
T="$1"; O="$2"; shift 2; mkdir -p "$O"; cd "$T" || exit 2
for f in "$@"; do
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  n=$(basename "$(dirname "$f")")__$(basename "$f" .py)
  /usr/bin/time -f "%e s" -o "$O/$n.time" "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --no-proof --no-typecheck $flags "$f" > "$O/$n.log" 2>&1
  rc=$?
  code=$(grep -o "PYCSL-[A-Z0-9-]*" "$O/$n.log" | head -1)
  msg=$(grep -A1 "PIPELINE ERROR" "$O/$n.log" | tail -1 | cut -c1-400)
  echo "$n rc=$rc $(cat $O/$n.time) ${code:-no-code} :: ${msg:-$(tail -1 $O/$n.log | cut -c1-120)}"
done
