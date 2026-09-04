#!/bin/bash
cd /home/fabrice/git/pycsl
export PATH=/home/fabrice/.opam/framac-coq8/bin:$PATH
grep "^  - " scratchpad/w9/suite_final.log | sed 's/^  - //' | sort -u > scratchpad/w9/failing_names.txt
: > scratchpad/w9/fail_causes.txt
while read -r n; do
  suite="${n%%/*}"; name="${n#*/}"
  f=$(find "test-suite/corpus/$suite" -name "$name.py" | head -1)
  [ -z "$f" ] && { echo -e "$n\tFILE-NOT-FOUND" >> scratchpad/w9/fail_causes.txt; continue; }
  flags=$(grep -m1 '^# pycsl-flags:' "$f" 2>/dev/null | sed 's/^# pycsl-flags://')
  out=$(timeout 120 .venv/bin/python3 src/pycsl/pycsl.py $flags "$f" 2>&1)
  if   echo "$out" | grep -q 'C-extension deny-list';        then c="IMPORT-DENYLIST"
  elif echo "$out" | grep -q 'Why3 Coq library not found';   then c="ROCQ-LIB-ABSENT"
  elif echo "$out" | grep -q 'PIPELINE ERROR';               then c="PIPELINE-ERROR: $(echo "$out"|grep -A1 'PIPELINE ERROR'|tail -1|cut -c1-70)"
  elif echo "$out" | grep -q 'but is expected to have type'; then c="L3-TC-TYPE-ERROR"
  elif echo "$out" | grep -q 'Timeout';                      then c="SMT-TIMEOUT"
  elif echo "$out" | grep -q 'Unknown';                      then c="SMT-UNKNOWN"
  elif echo "$out" | grep -q 'Verification SUCCESS';         then c="PROVES-ALONE (suite harness/flag difference)"
  else c="OTHER: $(echo "$out"|tail -1|cut -c1-70)"; fi
  echo -e "$n\t$c" >> scratchpad/w9/fail_causes.txt
done < scratchpad/w9/failing_names.txt
echo DONE >> scratchpad/w9/fail_causes.txt
