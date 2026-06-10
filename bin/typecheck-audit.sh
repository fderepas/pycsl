#!/usr/bin/env bash
# Phase D honest-gate audit (refactor.md): list the reference drivers whose emitted
# WhyML does NOT type-check (`pycsl --no-proof --typecheck` → "L3-tc ✗"). These are the
# dishonest SUCCESSes the typecheck gate exposes. See docs/typecheck-audit.md.
set -u
cd "$(dirname "$0")/.."
D=test-suite/corpus/pycsl-reference
PY=.venv/bin/python3
ok=0
fail=0
for f in "$D"/*.py; do
  b=$(basename "$f" .py)
  out=$(timeout 120 "$PY" src/pycsl/pycsl.py "$f" --no-proof --typecheck 2>&1)
  if echo "$out" | grep -q 'L3-tc ✓'; then
    ok=$((ok + 1))
  elif echo "$out" | grep -q 'L3-tc ✗'; then
    echo "$b: L3-tc FAIL"
    fail=$((fail + 1))
  fi
done
echo "typecheck audit: $ok type-check OK / $fail L3-tc FAIL (of the emitting drivers)"
