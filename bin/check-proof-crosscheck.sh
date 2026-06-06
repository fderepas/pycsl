#!/usr/bin/env bash
# check-proof-crosscheck.sh — proof2why3 mechanical 3-way cross-check
# gate (sticky-02.md Phase D).
#
# Walks every annotated Python file (`#@ proof rocq/lean …` citations)
# and invokes the proof2why3 IR-based cross-check on it. Aggregates
# PASS / SKIP / FAIL counts; non-zero exit on any FAIL.
#
# Files without `#@ proof ` directives are skipped (nothing to check).
# Citations targeting audit-anchor stubs (no `_AXIOM_REGISTRY` entry)
# count as SKIP, not FAIL — see crosscheck_ir.py:registry_skipped.

set -u
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

PYTHON="${PROJECT_ROOT}/.venv/bin/python"
if [ ! -x "$PYTHON" ]; then
    echo "[!] .venv/bin/python not found; run 'make .venv' first." >&2
    exit 2
fi

# Make sure the Coq switch is active (sertop / coqc resolution).
eval "$(opam env --switch=coq-4.14 2>/dev/null)" || true

total_pass=0
total_skip=0
total_fail=0
n_files=0
failed_files=()

# Files to check: self-annotate mirrors + reference corpus + module6_whyml
# + the extreme-rigor worked example (dual-prover Rocq + Lean).
candidates=(
    "src/self-annotate/src/"*.py
    "src/self-annotate/src/module6_whyml/"*.py
    "test-suite/corpus/pycsl-reference/"*.py
    "unix-filesystem/UnixInodeFileSystem.py"
)

for f in "${candidates[@]}"; do
    [ -f "$f" ] || continue
    # Skip files that don't cite anything (most files).
    grep -q "^#@ proof " "$f" || continue

    n_files=$((n_files + 1))
    out=$("$PYTHON" -m pycsl.proof2why3.crosscheck_ir "$f" 2>&1) || true
    summary_line=$(echo "$out" | tail -1)
    p=$(echo "$summary_line" | sed -n 's/.*[^0-9]\([0-9][0-9]*\) PASS.*/\1/p')
    s=$(echo "$summary_line" | sed -n 's/.*[^0-9]\([0-9][0-9]*\) SKIP.*/\1/p')
    fl=$(echo "$summary_line" | sed -n 's/.*[^0-9]\([0-9][0-9]*\) FAIL.*/\1/p')
    [ -z "$p" ]  && p=0
    [ -z "$s" ]  && s=0
    [ -z "$fl" ] && fl=0
    total_pass=$((total_pass + p))
    total_skip=$((total_skip + s))
    total_fail=$((total_fail + fl))

    if [ "$fl" -ne 0 ]; then
        failed_files+=("$f")
        echo "$out"
    fi
done

echo "=== Cross-check aggregate over $n_files annotated files ==="
echo "  PASS:  $total_pass"
echo "  SKIP:  $total_skip"
echo "  FAIL:  $total_fail"
if [ "$total_fail" -ne 0 ]; then
    echo "Failed files:"
    for f in "${failed_files[@]}"; do
        echo "  - $f"
    done
    exit 1
fi
exit 0
