#!/usr/bin/env bash
# Regression sweep: every gen #29 XFAIL witness must still be refused at the landed HEAD.
set -u
. /home/fabrice/git/pycsl/scratchpad/g29/env.sh
R=/home/fabrice/git/pycsl
cd $R/test-suite/corpus/pycsl-reference
n=0
for f in 1[45][0-9][0-9]_*.py 16[0-5][0-9]_*.py; do
  grep -q "pycsl-expected: FAIL" "$f" || continue
  n=$((n+1))
  fl=$(grep -m1 '^# pycsl-flags:' "$f" | sed 's/^# pycsl-flags://')
  out=$(timeout 400 $R/.venv/bin/python3 $R/src/pycsl/pycsl.py $fl "$f" 2>&1 | grep -E "Verification (SUCCESS|FAILED)" | tail -1)
  case "$out" in
    *SUCCESS*) echo "XPASS $f" ;;
  esac
done
rm -f $R/test-suite/corpus/pycsl-reference/*.mlw 2>/dev/null
echo "XFAIL-SWEEP-DONE $n witnesses $(date -u +%H:%M:%SZ)"
