#!/bin/bash
# tc-probes.sh <tree> <outdir> <prog.py>... : FULL PROOF verdict x3 memory models (admitted =
# typecheck OK, i.e. no refusal), cwd = the tree root. Honours `# pycsl-flags:`.
source /home/fabrice/git/pycsl/scratchpad/g29/env.sh  # why3 on PATH, PYTHONHASHSEED=0
T="$1"; O="$2"; shift 2; mkdir -p "$O"; cd "$T" || exit 2
for f in "$@"; do
  n=$(basename "$(dirname "$f")")__$(basename "$f" .py)
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  for mm in hoare typed store; do
    timeout 600 "$T/.venv/bin/python3" "$T/src/pycsl/pycsl.py" --memory-model $mm $flags "$f" > "$O/$n.$mm.log" 2>&1
    rc=$?
    v=$(grep -E "Verification SUCCESS|Verification FAILED|PIPELINE ERROR|typecheck|Type" "$O/$n.$mm.log" | tail -1 | cut -c1-160)
    m=$(grep -A1 "PIPELINE ERROR" "$O/$n.$mm.log" | tail -1 | cut -c1-200)
    echo "$n $mm rc=$rc :: $v ${m:+:: $m}" | tee -a "$O/summary.txt"
  done
done
