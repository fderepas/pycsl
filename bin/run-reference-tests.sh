#!/usr/bin/env bash
# Run pycsl on all Python test files in test-suite/corpus/pycsl-reference/ and report results.
#
# Usage:
#   run-reference-tests.sh                # run all tests
#   run-reference-tests.sh --start-at N   # skip tests before number N (e.g. 200 → start at 0200.py)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
TEST_DIR="$PROJECT_ROOT/test-suite/corpus/pycsl-reference"
PYCSL="python3 $PROJECT_ROOT/src/pycsl/pycsl.py"

START_AT=0
if [[ "${1:-}" == "--start-at" ]]; then
    if [[ -z "${2:-}" ]]; then
        echo "ERROR: --start-at requires a number"
        echo "Usage: $0 [--start-at N]"
        exit 1
    fi
    START_AT="$2"
    shift 2
fi

if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

passed=0
failed=0
errors=()

for py_file in "$TEST_DIR"/0*.py; do
    [ -f "$py_file" ] || continue
    name="$(basename "$py_file" .py)"

    # Skip files below --start-at threshold
    file_num=$(echo "$name" | sed 's/^0*//')
    file_num="${file_num:-0}"
    if [[ "$file_num" -lt "$START_AT" ]]; then
        continue
    fi

    # Extract extra flags from "# pycsl-flags: ..." comment in the file
    extra_flags=$(grep -m1 '^# pycsl-flags:' "$py_file" 2>/dev/null | sed 's/^# pycsl-flags://')

    # Check if this test is expected to fail
    expect_fail=$(grep -m1 '^# pycsl-expected: FAIL' "$py_file" 2>/dev/null)

    output=$($PYCSL $extra_flags "$py_file" 2>&1)
    if echo "$output" | grep -q "Verification SUCCESS"; then
        echo -e "${GREEN}[PASS]${RESET} $name"
        ((passed++))
    elif [ -n "$expect_fail" ]; then
        echo -e "${GREEN}[XFAIL]${RESET} $name (expected failure)"
        ((passed++))
    elif [ -z "$output" ]; then
        echo -e "${YELLOW}[SKIP]${RESET} $name (no output)"
        ((failed++))
        errors+=("$name (no output)")
    else
        echo -e "${RED}[FAIL]${RESET} $name"
        ((failed++))
        errors+=("$name")
    fi
done

total=$((passed + failed))

echo ""
echo "==============================="
echo " Results: $passed/$total passed"
echo "==============================="

if [ ${#errors[@]} -gt 0 ]; then
    echo "Failed/skipped:"
    for f in "${errors[@]}"; do
        echo "  - $f"
    done
fi

[ $failed -eq 0 ]
