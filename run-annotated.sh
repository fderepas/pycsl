#!/usr/bin/env bash
# Run pycsl on all Python test files in ./tests/manually_annotated/ and report results.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEST_DIR="$SCRIPT_DIR/tests/manually_annotated"
PYCSL="$SCRIPT_DIR/pycsl"

GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

passed=0
failed=0
errors=()

for py_file in "$TEST_DIR"/*.py; do
    [ -f "$py_file" ] || continue
    name="$(basename "$py_file")"

    if output=$("$PYCSL" "$py_file" 2>&1); then
        echo -e "${GREEN}[PASS]${RESET} $name"
        ((passed++))
    else
        echo -e "${RED}[FAIL]${RESET} $name"
        errors+=("$name")
        ((failed++))
    fi
done

total=$((passed + failed))

echo ""
echo "==============================="
echo " Results: $passed/$total passed"
echo "==============================="

if [ ${#errors[@]} -gt 0 ]; then
    echo "Failed tests:"
    for f in "${errors[@]}"; do
        echo "  - $f"
    done
fi

[ $failed -eq 0 ]
