#!/usr/bin/env bash
# Re-run gen #29's XFAIL witnesses under the TYPED memory model: any SUCCESS is a
# model-specific false proof the hoare-model repair did not cover.
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
R=/home/fabrice/git/pycsl
cd $R/test-suite/corpus/pycsl-reference
for f in 1[45][0-9][0-9]_*.py 16[0-5][0-9]_*.py; do
  grep -q "pycsl-expected: FAIL" "$f" || continue
  out=$(timeout 300 $R/.venv/bin/python3 $R/src/pycsl/pycsl.py --memory-model typed "$f" 2>&1 | grep -E "Verification (SUCCESS|FAILED)" | tail -1)
  case "$out" in
    *SUCCESS*) echo "TYPED-XPASS $f" ;;
  esac
done
rm -f $R/test-suite/corpus/pycsl-reference/*.mlw 2>/dev/null
echo TYPED-SWEEP-DONE $(date -u +%H:%M:%SZ)
