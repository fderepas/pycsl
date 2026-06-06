#!/usr/bin/env bash
# extraction-byte-diff-upward.sh — Q4 U.4 byte-diff (upward direction).
#
# Pipeline per `.py` source:
#   1. Module 5 (via pycsl-ir-dump.py) → IR JSON file.
#   2. Extracted Rocq ir_to_stmt (via OCaml ir_driver) consumes JSON.
#   3. Result is PASS iff:
#        - validate_ir returns true, AND
#        - ir_to_stmt returns Some(...) on the first function's body.
#
# Cases outside the converter's subset return ir_to_stmt=None — that's
# expected; they're tallied as SKIP, not FAIL.
#
# A real failure is: valid=true but ir_to_stmt=None on a subset case,
# OR validate_ir=false on a case that should validate.

set -u
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROCQ="${ROOT}/src/formal-semantics/rocq"
EXTRACTED="${ROCQ}/extracted"
CASES_DIR="${1:-${ROOT}/test-suite/extraction-byte-diff/reference-cases}"
PY_VENV="${ROOT}/.venv/bin/python"

DRIVER="${EXTRACTED}/ir_driver"

if [ ! -x "$DRIVER" ]; then
  echo "[!] ir_driver not built; rebuilding..."
  (cd "$EXTRACTED" && \
   ocamlfind ocamlc -package yojson -linkpkg \
     IrToStmtExtract.ml ir_driver.ml -o ir_driver) \
   2>&1 | tail -5
fi

if [ ! -x "$DRIVER" ]; then
  echo "[!] FAILED to build ir_driver"
  exit 2
fi

PASS=0
SKIP=0
FAIL_DRIVER=0      # ir_to_stmt subset miss (counts as "outside subset")
FAIL_M5=0          # Module 5 itself could not process the file
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT

for py_file in "${CASES_DIR}"/*.py; do
  case_id="$(basename "${py_file%.py}")"
  json_file="${WORK}/${case_id}.json"

  # Step 1: run Module 5 to produce IR JSON.
  if ! "$PY_VENV" "${ROOT}/bin/pycsl-ir-dump.py" "$py_file" \
       > "$json_file" 2>/dev/null; then
    echo "M5FAIL ${case_id}: Module 5 failed to dump IR"
    FAIL_M5=$((FAIL_M5+1))
    continue
  fi

  # Step 2: run the OCaml driver.
  result_line="$("$DRIVER" "$case_id" "$json_file" 2>&1)"
  echo "$result_line"

  # Step 3: classify.
  if echo "$result_line" | grep -q "ir_to_stmt=Some"; then
    PASS=$((PASS+1))
  elif echo "$result_line" | grep -q "ir_to_stmt=None"; then
    SKIP=$((SKIP+1))
  elif echo "$result_line" | grep -q "ir_to_stmt=SKIP"; then
    SKIP=$((SKIP+1))
  else
    FAIL_DRIVER=$((FAIL_DRIVER+1))
  fi
done

TOTAL=$((PASS+SKIP+FAIL_DRIVER+FAIL_M5))
echo ""
echo "================================="
echo " Q4 U.4 upward byte-diff results"
echo "================================="
echo " PASS:       ${PASS}/${TOTAL} (ir_to_stmt returned Some)"
echo " SKIP:       ${SKIP}/${TOTAL} (outside ir_to_stmt subset)"
echo " FAIL_DRIVER:${FAIL_DRIVER}/${TOTAL} (driver returned unexpected output)"
echo " FAIL_M5:    ${FAIL_M5}/${TOTAL} (Module 5 could not produce IR)"
echo ""
echo "Tip: for blocker breakdown, redirect output to a file then:"
echo "     grep -oE \"blocker:[A-Za-z_]+\" <file> | sort | uniq -c | sort -rn"

[ "$FAIL_DRIVER" -eq 0 ]
