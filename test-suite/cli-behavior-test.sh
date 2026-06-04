#!/bin/bash
# CLI-behavior regression test for src/pycsl/pycsl.py's argument handling and main()
# control flow (exit codes + key output markers). This is the behavior gate the WhyML
# emission differential cannot cover, since main()/argparse is CLI orchestration, not
# WhyML emission. Run from anywhere; set PYTHON to the interpreter that can import lark
# (e.g. the project .venv): `PYTHON=.venv/bin/python test-suite/cli-behavior-test.sh`.
set -u
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PY="${PYTHON:-python3}"
PYCSL="$PY $ROOT/src/pycsl/pycsl.py"
C="$ROOT/test-suite/corpus/pycsl-reference"
fails=0

# check <label> <expected-exit> <expected-marker-regex|-> -- <pycsl args...>
check() {
  local label="$1" exp_ec="$2" exp_mark="$3"; shift 4   # drop the literal "--"
  local out ec
  out=$($PYCSL "$@" 2>&1); ec=$?
  local ok=1
  [ "$ec" = "$exp_ec" ] || ok=0
  if [ "$exp_mark" != "-" ] && ! echo "$out" | grep -qE "$exp_mark"; then ok=0; fi
  if [ "$ok" = 1 ]; then
    echo "  ok   $label (exit=$ec)"
  else
    echo "  FAIL $label: exit=$ec (expected $exp_ec), marker /$exp_mark/ not matched"
    fails=$((fails+1))
  fi
}

echo "=== PyCSL CLI behavior test ==="
check 01_missing_file   1 "not found"             -- /tmp/__pycsl_no_such_file__.py --no-proof
check 02_pass_noproof   0 "Verification SUCCESS"  -- "$C/0457.py" --no-proof
check 03_pipeline_error 1 "PIPELINE ERROR"        -- "$C/0462.py" --no-proof
check 04_mm_hoare       0 "Verification SUCCESS"  -- "$C/0457.py" --no-proof --memory-model hoare
check 05_mm_typed       0 "Verification SUCCESS"  -- "$C/0457.py" --no-proof --memory-model typed
check 06_keep_mlw       0 "Verification SUCCESS"  -- "$C/0457.py" --no-proof --keep-mlw
rm -f "$C/0457.mlw"
check 07_audit_clean    0 "-"                     -- "$C/0457.py" --audit-proof
check 08_help           0 "usage:"                -- --help
check 09_bogus_flag     2 "-"                     -- "$C/0457.py" --bogus-zzz
check 10_no_file        2 "-"                     --

# --help must still register all 21 options (grouping must not drop any).
optcount=$($PYCSL --help 2>&1 | grep -cE '^\s+(-|--)')
if [ "$optcount" = 21 ]; then
  echo "  ok   11_help_optcount (21)"
else
  echo "  FAIL 11_help_optcount: $optcount (expected 21)"; fails=$((fails+1))
fi

echo "==============================="
if [ "$fails" = 0 ]; then echo "CLI behavior: PASS"; exit 0; else echo "CLI behavior: FAIL ($fails)"; exit 1; fi
