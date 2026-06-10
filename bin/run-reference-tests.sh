#!/usr/bin/env bash
# Run pycsl on all Python test files in both reference test suites and report results.
#
# Usage:
#   run-reference-tests.sh                        # run all tests (both suites)
#   run-reference-tests.sh --python               # run only python-reference tests
#   run-reference-tests.sh --pycsl                # run only pycsl-reference tests
#   run-reference-tests.sh --start-at N           # skip tests before number N
#   run-reference-tests.sh --stop-at N            # stop after test number N
#   run-reference-tests.sh --jobs K               # run K tests concurrently
#                                                 # (default = half the machine's cores)
#   run-reference-tests.sh --jobs 1               # serial (identical to the old behaviour)
#
# Parallelism (more-proc.md): tests are independent (each its own process, read-only src,
# test-unique .mlw/.proofs outputs), so they fan out across cores via `xargs -P`. The default
# job count is EXACTLY half the machine's logical cores (get_cpu_count/2) — a courtesy budget
# that leaves the other half for a second agent / interactive work, and that matches the two
# provers (alt-ergo + z3) each test's `why3` spawns. Output order and the pass/fail summary are
# deterministic regardless of completion order. PYCSL_JOBS overrides the default; --jobs wins.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYCSL_DIR="$PROJECT_ROOT/test-suite/corpus/pycsl-reference"
PYTHON_DIR="$PROJECT_ROOT/test-suite/corpus/python-reference"

# Prefer the project venv's python so workers need no `activate` (why3 is a system tool).
if [ -x "$PROJECT_ROOT/.venv/bin/python3" ]; then
    PY="$PROJECT_ROOT/.venv/bin/python3"
else
    PY="python3"
fi
PYCSL="$PY $PROJECT_ROOT/src/pycsl/pycsl.py"

# get_cpu_count / half_cpu_jobs — single source of truth (more-proc.md §4.5), shared with
# bin/byte-diff-sweep.sh so no copy drifts. (Was inline here; factored into lib-cpu.sh.)
source "$SCRIPT_DIR/lib-cpu.sh"

# Derive the suite name (the corpus subdir) from a test file's path.
_suite_of() {
    case "$1" in
        *"/pycsl-reference/"*) echo "pycsl-reference" ;;
        *"/python-reference/"*) echo "python-reference" ;;
        *) basename "$(dirname "$1")" ;;
    esac
}

# A stable per-file result key (path with non-alnum → _), so concurrent workers never collide
# even across suites that share numbering (pycsl-reference/0001 vs python-reference/0001).
_key_of() { echo "$1" | tr -c 'A-Za-z0-9' '_'; }

# ── Worker mode: run ONE test, classify, write its result file. Always exits 0 (status is in
#    the file, not the exit code) so xargs never aborts the fan-out. ────────────────────────
if [ "${1:-}" = "--worker" ]; then
    py_file="$2"
    name="$(basename "$py_file" .py)"
    extra_flags=$(grep -m1 '^# pycsl-flags:' "$py_file" 2>/dev/null | sed 's/^# pycsl-flags://')
    expect_fail=$(grep -m1 '^# pycsl-expected: FAIL' "$py_file" 2>/dev/null)

    output=$($PYCSL $extra_flags "$py_file" 2>&1)
    if echo "$output" | grep -q "Verification SUCCESS"; then
        status=PASS
    elif [ -n "$expect_fail" ]; then
        status=XFAIL
    elif [ -z "$output" ]; then
        status=SKIP
    else
        status=FAIL
    fi
    printf '%s\n' "$status" > "$RESULTS_DIR/$(_key_of "$py_file")"
    exit 0
fi

# ── Main mode ──────────────────────────────────────────────────────────────────────────────
TEST_DIRS=("$PYCSL_DIR" "$PYTHON_DIR")

usage() {
    echo "Usage: $0 [--python] [--pycsl] [--start-at N] [--stop-at N] [--jobs K]"
    echo ""
    echo "  (no flags)      run both pycsl-reference and python-reference suites"
    echo "  --python        run only test-suite/corpus/python-reference"
    echo "  --pycsl         run only test-suite/corpus/pycsl-reference"
    echo "  --start-at N    skip tests numbered below N"
    echo "  --stop-at N     stop after test number N"
    echo "  --jobs K        run K tests concurrently (default: half the cores; 1 = serial)"
}

START_AT=0
STOP_AT=""
JOBS_FLAG=""
while [[ $# -gt 0 ]]; do
    case "$1" in
        --python) TEST_DIRS=("$PYTHON_DIR"); shift ;;
        --pycsl)  TEST_DIRS=("$PYCSL_DIR"); shift ;;
        --start-at)
            if [[ -z "${2:-}" ]]; then echo "ERROR: --start-at requires a number"; usage; exit 1; fi
            START_AT="$2"; shift 2 ;;
        --stop-at)
            if [[ -z "${2:-}" ]]; then echo "ERROR: --stop-at requires a number"; usage; exit 1; fi
            STOP_AT="$2"; shift 2 ;;
        --jobs)
            if [[ -z "${2:-}" ]]; then echo "ERROR: --jobs requires a number"; usage; exit 1; fi
            JOBS_FLAG="$2"; shift 2 ;;
        -h|--help) usage; exit 0 ;;
        *) echo "ERROR: unknown option '$1'"; usage; exit 1 ;;
    esac
done

if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

# Concurrency: half the cores by default (more-proc.md). --jobs beats PYCSL_JOBS beats the default.
CORES=$(get_cpu_count)
JOBS=$(( CORES / 2 ))
[ "$JOBS" -lt 1 ] && JOBS=1
JOBS="${PYCSL_JOBS:-$JOBS}"
[ -n "$JOBS_FLAG" ] && JOBS="$JOBS_FLAG"

# Stdlib-coverage CI gate (workplan PR 7). Runs ONCE before any corpus test so a coverage
# drift fails fast. Skip with PYCSL_SKIP_STDLIB_CHECK=1.
if [ "${PYCSL_SKIP_STDLIB_CHECK:-0}" != "1" ]; then
    if ! python3 "$PROJECT_ROOT/bin/stdlib-coverage.py" --check all; then
        echo ""
        echo "[!] stdlib-coverage --check failed. Either:"
        echo "    1. Update calls-english.md / calls-pycsl.md / src/pycsl_lib/ to match the report, OR"
        echo "    2. Regenerate the report with --discover after intentional code changes."
        echo "    Skip this gate temporarily with PYCSL_SKIP_STDLIB_CHECK=1."
        exit 1
    fi
fi

# Doc-coherency CI gate. Skip temporarily with PYCSL_SKIP_DOC_COHERENCY_CHECK=1.
if [ "${PYCSL_SKIP_DOC_COHERENCY_CHECK:-0}" != "1" ]; then
    if ! python3 "$PROJECT_ROOT/bin/doc-coherency.py" --check >/dev/null; then
        echo ""
        echo "[!] doc-coherency --check failed. A #@ directive is missing"
        echo "    from at least one normative surface (README, annotations.md,"
        echo "    docs/pycsl-*reference*.md). Run"
        echo "        ./bin/doc-coherency.py --check"
        echo "    for the per-directive grid. Skip with"
        echo "    PYCSL_SKIP_DOC_COHERENCY_CHECK=1."
        exit 1
    fi
fi

# IR conformance CI gate (docs/ir.md §10; refactor.md Phase E). Runs BOTH conformance
# corpora — core-only (golden IR -> WhyML) and front-end-only (source -> resolved IR) —
# so a standard gate run fails if the frozen front-end<->core contract regresses. Additive:
# runs ONCE before corpus discovery, does not touch the reference-test counting. Skip
# temporarily with PYCSL_SKIP_CONFORMANCE_CHECK=1.
if [ "${PYCSL_SKIP_CONFORMANCE_CHECK:-0}" != "1" ]; then
    if ! "$PROJECT_ROOT/bin/run-conformance.sh"; then
        echo ""
        echo "[!] IR conformance failed. Either the core no longer re-derives the golden"
        echo "    WhyML (core-only corpus), or the front-end no longer produces the canonical"
        echo "    IR (front-end-only corpus). The IR is frozen at v1.1 (docs/ir.md §10): a"
        echo "    deliberate shape change requires an IR_VERSION/ACCEPTED_IR_VERSIONS bump and"
        echo "    refreshed goldens. Run ./bin/run-conformance.sh for the per-corpus detail."
        echo "    Skip this gate temporarily with PYCSL_SKIP_CONFORMANCE_CHECK=1."
        exit 1
    fi
fi

GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[0;33m'
RESET='\033[0m'

# Build the ordered list of test files (same discovery + start/stop logic as before).
entries=()   # parallel arrays: entry i = file path; suite/name derived on read
for dir in "${TEST_DIRS[@]}"; do
    py_files=()
    for f in "$dir"/0*.py; do
        [ -f "$f" ] && py_files+=("$f")
    done
    if [ -d "$dir/stdlib" ]; then
        while IFS= read -r f; do py_files+=("$f"); done \
            < <(find "$dir/stdlib" -name "*.py" -type f | sort)
    fi
    for py_file in "${py_files[@]}"; do
        [ -f "$py_file" ] || continue
        name="$(basename "$py_file" .py)"
        file_num=$(echo "$name" | sed 's/^0*//'); file_num="${file_num:-0}"
        [[ "$file_num" -lt "$START_AT" ]] && continue
        if [[ -n "$STOP_AT" && "$file_num" -gt "$STOP_AT" ]]; then break; fi
        entries+=("$py_file")
    done
done

echo "[*] $((${#entries[@]})) tests across ${#TEST_DIRS[@]} suite(s); jobs=$JOBS (cores=$CORES)"

RESULTS_DIR="$(mktemp -d)"
export RESULTS_DIR PYCSL
trap 'rm -rf "$RESULTS_DIR"' EXIT

# Fan out: each file → a worker (re-exec of this script in --worker mode), K at a time.
printf '%s\0' "${entries[@]}" | xargs -0 -P "$JOBS" -I {} "$0" --worker {}

# Aggregate by iterating `entries` IN ORDER (deterministic output identical to the serial run),
# reading each worker's result file. Completion order is irrelevant.
passed=0
failed=0
errors=()
failed_files=()      # paths that failed in the parallel pass (for the confirmation re-run)
current_suite=""
for py_file in "${entries[@]}"; do
    suite="$(_suite_of "$py_file")"
    if [ "$suite" != "$current_suite" ]; then
        echo "--- $suite ---"
        current_suite="$suite"
    fi
    name="$(basename "$py_file" .py)"
    status="$(cat "$RESULTS_DIR/$(_key_of "$py_file")" 2>/dev/null)"
    case "$status" in
        PASS)  echo -e "${GREEN}[PASS]${RESET} $name"; ((passed++)) ;;
        XFAIL) echo -e "${GREEN}[XFAIL]${RESET} $name (expected failure)"; ((passed++)) ;;
        SKIP)  echo -e "${YELLOW}[SKIP]${RESET} $name (no output)"; ((failed++)); errors+=("$suite/$name (no output)"); failed_files+=("$py_file") ;;
        FAIL)  echo -e "${RED}[FAIL]${RESET} $name"; ((failed++)); errors+=("$suite/$name"); failed_files+=("$py_file") ;;
        *)     echo -e "${RED}[FAIL]${RESET} $name (no result)"; ((failed++)); errors+=("$suite/$name (no result)"); failed_files+=("$py_file") ;;
    esac
done

# Confirmation pass: a parallel run can suffer a *spurious* prover timeout when the box is
# saturated (e.g. another agent is also sweeping → load > cores). Re-run each failure SERIALLY,
# one at a time with no intra-sweep contention; any that now passes was a load-induced flake, not
# a regression. This keeps the parallel sweep trustworthy under concurrent load. Skip in serial
# mode (JOBS=1: nothing to disambiguate) or via PYCSL_NO_RECONFIRM=1.
if [ ${#failed_files[@]} -gt 0 ] && [ "$JOBS" -gt 1 ] && [ "${PYCSL_NO_RECONFIRM:-0}" != "1" ]; then
    echo ""
    echo "[*] Re-running ${#failed_files[@]} failure(s) serially to rule out load-induced timeouts..."
    recovered=()
    confirmed=()
    for py_file in "${failed_files[@]}"; do
        name="$(basename "$py_file" .py)"
        "$0" --worker "$py_file"     # rewrites this test's result file, no contention
        status="$(cat "$RESULTS_DIR/$(_key_of "$py_file")" 2>/dev/null)"
        if [ "$status" = "PASS" ] || [ "$status" = "XFAIL" ]; then
            echo -e "  ${YELLOW}[FLAKY→PASS]${RESET} $name (failed under parallel load, passes serially)"
            recovered+=("$name"); ((passed++)); ((failed--))
        else
            echo -e "  ${RED}[CONFIRMED FAIL]${RESET} $name"
            confirmed+=("$(_suite_of "$py_file")/$name")
        fi
    done
    errors=("${confirmed[@]}")
    if [ ${#recovered[@]} -gt 0 ]; then
        echo "[*] ${#recovered[@]} flaky timeout(s) recovered on serial re-run (not regressions)."
    fi
fi

total=$((passed + failed))

echo ""
echo "==============================="
echo " Results: $passed/$total passed"
echo "==============================="

if [ ${#errors[@]} -gt 0 ]; then
    echo "Failed/skipped (confirmed):"
    for f in "${errors[@]}"; do
        echo "  - $f"
    done
fi

[ $failed -eq 0 ]
