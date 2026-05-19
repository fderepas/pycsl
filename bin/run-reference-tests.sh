#!/usr/bin/env bash
# Run pycsl on all Python test files in both reference test suites and report results.
#
# Usage:
#   run-reference-tests.sh                        # run all tests (both suites)
#   run-reference-tests.sh --python               # run only python-reference tests
#   run-reference-tests.sh --pycsl                # run only pycsl-reference tests
#   run-reference-tests.sh --start-at N           # skip tests before number N
#   run-reference-tests.sh --stop-at N            # stop after test number N
#   run-reference-tests.sh --start-at N --stop-at M  # run tests from N to M inclusive

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYCSL_DIR="$PROJECT_ROOT/test-suite/corpus/pycsl-reference"
PYTHON_DIR="$PROJECT_ROOT/test-suite/corpus/python-reference"
TEST_DIRS=("$PYCSL_DIR" "$PYTHON_DIR")
PYCSL="python3 $PROJECT_ROOT/src/pycsl/pycsl.py"

usage() {
    echo "Usage: $0 [--python] [--pycsl] [--start-at N] [--stop-at N]"
    echo ""
    echo "  (no flags)      run both pycsl-reference and python-reference suites"
    echo "  --python        run only test-suite/corpus/python-reference"
    echo "  --pycsl         run only test-suite/corpus/pycsl-reference"
    echo "  --start-at N    skip tests numbered below N"
    echo "  --stop-at N     stop after test number N"
}

START_AT=0
STOP_AT=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --python)
            TEST_DIRS=("$PYTHON_DIR")
            shift
            ;;
        --pycsl)
            TEST_DIRS=("$PYCSL_DIR")
            shift
            ;;
        --start-at)
            if [[ -z "${2:-}" ]]; then
                echo "ERROR: --start-at requires a number"
                usage; exit 1
            fi
            START_AT="$2"
            shift 2
            ;;
        --stop-at)
            if [[ -z "${2:-}" ]]; then
                echo "ERROR: --stop-at requires a number"
                usage; exit 1
            fi
            STOP_AT="$2"
            shift 2
            ;;
        -h|--help)
            usage; exit 0
            ;;
        *)
            echo "ERROR: unknown option '$1'"
            usage; exit 1
            ;;
    esac
done

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

for dir in "${TEST_DIRS[@]}"; do
    suite_name="$(basename "$dir")"
    echo "--- $suite_name ---"
    for py_file in "$dir"/0*.py; do
        [ -f "$py_file" ] || continue
        name="$(basename "$py_file" .py)"

        # Skip files below --start-at threshold
        file_num=$(echo "$name" | sed 's/^0*//')
        file_num="${file_num:-0}"
        if [[ "$file_num" -lt "$START_AT" ]]; then
            continue
        fi

        # Stop after --stop-at threshold
        if [[ -n "$STOP_AT" && "$file_num" -gt "$STOP_AT" ]]; then
            break
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
            errors+=("$suite_name/$name (no output)")
        else
            echo -e "${RED}[FAIL]${RESET} $name"
            ((failed++))
            errors+=("$suite_name/$name")
        fi
    done
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
