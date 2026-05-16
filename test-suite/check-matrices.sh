#!/usr/bin/env bash
# check-matrices.sh — Verify traceability matrices against actual pycsl results.
#
# For each row in traceability-python.md and traceability-pycsl.md,
# runs the corresponding test through pycsl and checks whether the
# actual outcome matches the recorded status.
#
# Usage:
#   bash test-suite/check-matrices.sh [--python-only | --pycsl-only] [--update]
#
# Options:
#   --python-only   Only check the Python reference matrix
#   --pycsl-only    Only check the PyCSL reference matrix
#   --update        Rewrite the matrix files with actual statuses
#
# Exit code: 0 if all statuses match, 1 if any mismatch found.

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
if [ -x "$REPO_DIR/.venv/bin/pycsl" ]; then
    PYCSL="$REPO_DIR/.venv/bin/pycsl"
elif command -v pycsl >/dev/null 2>&1; then
    PYCSL="$(command -v pycsl)"
else
    echo "ERROR: pycsl binary not found. Install with: pip install -e ." >&2
    exit 1
fi
TIMEOUT=60

PYTHON_MATRIX="$SCRIPT_DIR/traceability-python.md"
PYCSL_MATRIX="$SCRIPT_DIR/traceability-pycsl.md"
PYTHON_CORPUS="$SCRIPT_DIR/corpus/python-reference"
PYCSL_CORPUS="$SCRIPT_DIR/corpus/pycsl-reference"

do_python=true
do_pycsl=true
do_update=false

for arg in "$@"; do
    case "$arg" in
        --python-only) do_pycsl=false ;;
        --pycsl-only)  do_python=false ;;
        --update)      do_update=true ;;
        -h|--help)
            sed -n '2,/^$/{ s/^# //; s/^#$//; p }' "$0"
            exit 0 ;;
        *) echo "Unknown option: $arg"; exit 2 ;;
    esac
done

# ---------- helpers ----------

# Classify pycsl output into a status string.
# Args: $1 = test file path, remaining args = extra pycsl flags
classify() {
    local test_file="$1"; shift

    local output
    local exit_code=0
    output="$(timeout "$TIMEOUT" "$PYCSL" "$@" "$test_file" 2>&1)" || exit_code=$?

    # timeout(1) returns 124 on timeout
    if [[ $exit_code -eq 124 ]]; then
        echo "UNPROVEN"
        return
    fi

    if echo "$output" | grep -q "Verification SUCCESS"; then
        echo "PASS"
        return
    fi

    # Check for parse / grammar errors (FAIL)
    if echo "$output" | grep -qiE "Parse error|SyntaxError|UnexpectedToken|Unexpected token|Previous tokens:"; then
        echo "FAIL"
        return
    fi

    # Check for pipeline errors / tracebacks (BUG)
    if echo "$output" | grep -qE "UNEXPECTED PIPELINE ERROR|Traceback|Exception|ghost modification|type mismatch|syntax error|illegal character"; then
        echo "BUG"
        return
    fi

    # Check for solver timeout / unknown (UNPROVEN)
    if echo "$output" | grep -qE "Unknown \(sat\)|Unknown \(unknown\)|Timeout|termination.*cannot be proved"; then
        echo "UNPROVEN"
        return
    fi

    # FAILED with no further detail
    if echo "$output" | grep -q "FAILED"; then
        echo "BUG"
        return
    fi

    # Fallback
    echo "BUG"
}

# Detect memory model from the test file's docstring (PyCSL Annotation Reference 5.2/5.3)
detect_memory_model_flags() {
    local test_file="$1"
    local header
    header="$(head -1 "$test_file")"
    if echo "$header" | grep -q "Annotation Reference 5\.2"; then
        echo "--memory-model typed"
    elif echo "$header" | grep -q "Annotation Reference 5\.3"; then
        echo "--memory-model store"
    fi
}

# Detect extra pycsl CLI flags from a "# pycsl-flags: ..." comment in the test file.
detect_extra_pycsl_flags() {
    local test_file="$1"
    grep -m1 '^# pycsl-flags:' "$test_file" 2>/dev/null | sed 's/^# pycsl-flags://' || true
}

# Check whether recorded and actual statuses are considered matching.
# UNSUPPORTED is a human label — any non-PASS result is acceptable.
statuses_match() {
    local recorded="$1"
    local actual="$2"
    if [[ "$recorded" == "$actual" ]]; then
        return 0
    fi
    # UNSUPPORTED: anything that isn't PASS counts as matching
    if [[ "$recorded" == "UNSUPPORTED" && "$actual" != "PASS" ]]; then
        return 0
    fi
    return 1
}

# ---------- check one matrix ----------

# Global counters
grand_total=0
grand_match=0
grand_mismatch=0

# check_matrix MATRIX_FILE CORPUS_DIR LABEL
check_matrix() {
    local matrix="$1"
    local corpus="$2"
    local label="$3"

    if [[ ! -f "$matrix" ]]; then
        echo "  ⚠  Matrix file not found: $matrix"
        return
    fi

    local total=0 match=0 mismatch=0 skipped=0
    local mismatches=()
    local updated_lines=()

    while IFS= read -r line; do
        # Only process table data rows (| digit...)
        if ! echo "$line" | grep -qE '^\| [0-9]'; then
            updated_lines+=("$line")
            continue
        fi

        # Parse columns: $2=ref, $(NF-2)=test_id, $(NF-1)=status (handles \| in cells)
        local ref test_id recorded_status
        ref="$(echo "$line" | awk -F'|' '{gsub(/^ +| +$/,"",$2); print $2}')"
        test_id="$(echo "$line" | awk -F'|' '{gsub(/^ +| +$/,"",$(NF-2)); print $(NF-2)}')"
        recorded_status="$(echo "$line" | awk -F'|' '{gsub(/^ +| +$/,"",$(NF-1)); print $(NF-1)}')"

        # Handle comma-separated test IDs (e.g. "0001, 0066, 0067")
        local -a test_ids_arr
        IFS=',' read -ra test_ids_arr <<< "$test_id"

        local row_ok=true
        local any_file_found=false
        local first_actual=""

        for tid in "${test_ids_arr[@]}"; do
            tid="$(echo "$tid" | tr -d ' ')"
            local test_file="$corpus/${tid}.py"
            if [[ ! -f "$test_file" ]]; then
                echo "  ⚠  Test file missing: $test_file (ref $ref)"
                continue
            fi
            any_file_found=true

            # Extra pycsl flags (memory model detection + pycsl-flags comment)
            local extra_flags
            extra_flags="$(detect_memory_model_flags "$test_file")"
            local pycsl_flags
            pycsl_flags="$(detect_extra_pycsl_flags "$test_file")"
            extra_flags="$extra_flags $pycsl_flags"

            # Run and classify
            local actual_status
            # shellcheck disable=SC2086
            actual_status="$(classify "$test_file" $extra_flags)"

            if [[ -z "$first_actual" ]]; then
                first_actual="$actual_status"
            fi

            if ! statuses_match "$recorded_status" "$actual_status"; then
                row_ok=false
                first_actual="$actual_status"
                break
            fi
        done

        if [[ "$any_file_found" != "true" ]]; then
            updated_lines+=("$line")
            ((skipped++)) || true
            continue
        fi

        ((total++)) || true

        if $row_ok; then
            ((match++)) || true
            updated_lines+=("$line")
        else
            ((mismatch++)) || true
            mismatches+=("  $ref ($test_id): recorded=$recorded_status actual=$first_actual")
            local new_line
            new_line="$(echo "$line" | sed "s/| *${recorded_status} *|$/| ${first_actual} |/")"
            updated_lines+=("$new_line")
        fi

        # Progress indicator (overwrite line)
        printf "\r  [%s] %d/%d tested (%d ok, %d mismatch)" \
            "$label" "$total" "$total" "$match" "$mismatch" >&2
    done < "$matrix"

    # Clear progress line
    printf "\r%-60s\r" "" >&2

    echo "  [$label] $total tests: $match match, $mismatch mismatch, $skipped skipped"
    if ((mismatch > 0)); then
        echo "  Mismatches:"
        for m in "${mismatches[@]}"; do
            echo "    $m"
        done
    fi

    if $do_update && ((mismatch > 0)); then
        printf '%s\n' "${updated_lines[@]}" > "$matrix"
        echo "  ✏  Updated $matrix with actual statuses"
    fi

    grand_total=$((grand_total + total))
    grand_match=$((grand_match + match))
    grand_mismatch=$((grand_mismatch + mismatch))
}

# ---------- main ----------

echo "╔══════════════════════════════════════════════╗"
echo "║   Traceability Matrix Verification           ║"
echo "╚══════════════════════════════════════════════╝"
echo ""

if $do_python; then
    echo "▸ Checking Python Reference matrix..."
    check_matrix "$PYTHON_MATRIX" "$PYTHON_CORPUS" "Python"
    echo ""
fi

if $do_pycsl; then
    echo "▸ Checking PyCSL Reference matrix..."
    check_matrix "$PYCSL_MATRIX" "$PYCSL_CORPUS" "PyCSL"
    echo ""
fi

echo "═══════════════════════════════════════════════"
echo "  Total: $grand_total | Match: $grand_match | Mismatch: $grand_mismatch"
echo "═══════════════════════════════════════════════"

if ((grand_mismatch > 0)); then
    echo "✗ $grand_mismatch status mismatch(es) found."
    exit 1
else
    echo "✓ All recorded statuses match actual results."
    exit 0
fi
