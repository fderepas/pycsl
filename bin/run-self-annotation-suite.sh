#!/usr/bin/env bash
# Self-annotation suite — workplan PR 9, §9.1.
#
# Runs `pycsl` on a designated set of `src/pycsl/` modules and exits 1
# on any failure. The suite is the acceptance criterion of the
# StdlibCoverage workplan: the stubs are *useful* iff this suite proves.
#
# Adding a module to the suite is a deliberate act — not automatic.
# Each addition validates that the per-PR stub additions are
# sufficient for the module's surface area.
#
# Current suite (workplan §9.1 — "tractable now"):
#   src/pycsl/errors.py     — pure exception classes + class invariant
#
# Next candidates (workplan §9.1 — pending richer stubs):
#   src/pycsl/ir_schema.py  — needs dict-membership and isinstance
#                             stubs with non-trivial postconditions.

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
PYCSL="python3 $PROJECT_ROOT/src/pycsl/pycsl.py"

if [ -f "$PROJECT_ROOT/.venv/bin/activate" ]; then
    source "$PROJECT_ROOT/.venv/bin/activate"
fi

SUITE=(
    # Bucket A — tractable now (full proof or \trusted with proof-passing stub)
    "src/pycsl/errors.py"
    "src/self-annotate/src/errors.py"
    "src/self-annotate/src/ir_schema.py"
    "src/self-annotate/src/exception_model.py"
    "src/self-annotate/src/module6_whyml/identifiers.py"
    "src/self-annotate/src/module6_whyml/scc.py"
    "src/self-annotate/src/module6_whyml/abstract_ops.py"
    "src/self-annotate/src/module6_whyml/types.py"
    "src/self-annotate/src/module6_whyml/functions.py"
    "src/self-annotate/src/module6_whyml/ir_scanner.py"
    "src/self-annotate/src/__init__.py"
    "src/self-annotate/src/module6_whyml/__init__.py"
    # Bucket B — needs richer stubs; currently \trusted with stub bodies
    "src/self-annotate/src/import_classifier.py"
    "src/self-annotate/src/ConcurrencyChecker.py"
    # Bucket C — research-grade, \trusted reviewer with stub bodies
    "src/self-annotate/src/audit_proof.py"
    "src/self-annotate/src/Module1_Ingestor.py"
    "src/self-annotate/src/Module2_Parser.py"
    "src/self-annotate/src/Module3_Weaver.py"
    "src/self-annotate/src/Module4_SemanticAnalyzer.py"
    "src/self-annotate/src/Module5_IREmitter.py"
    "src/self-annotate/src/Module6_WhyMLTranspiler.py"
    "src/self-annotate/src/pycsl.py"
    "src/self-annotate/src/module6_whyml/auto_trust.py"
    "src/self-annotate/src/module6_whyml/expressions.py"
    "src/self-annotate/src/module6_whyml/statements.py"
    "src/self-annotate/src/module6_whyml/preamble.py"
)

GREEN='\033[0;32m'
RED='\033[0;31m'
RESET='\033[0m'

passed=0
failed=0
errors=()

echo "--- self-annotation suite ---"
for rel in "${SUITE[@]}"; do
    path="$PROJECT_ROOT/$rel"
    if [ ! -f "$path" ]; then
        echo -e "${RED}[MISSING]${RESET} $rel"
        errors+=("$rel (file missing)")
        ((failed++))
        continue
    fi
    output=$($PYCSL "$path" 2>&1)
    if echo "$output" | grep -q "Verification SUCCESS"; then
        echo -e "${GREEN}[PASS]${RESET} $rel"
        ((passed++))
    else
        echo -e "${RED}[FAIL]${RESET} $rel"
        echo "$output" | tail -10
        errors+=("$rel")
        ((failed++))
    fi
done

total=$((passed + failed))
echo ""
echo "==============================="
echo " Self-annotation: $passed/$total proved"
echo "==============================="

if [ $failed -gt 0 ]; then
    echo "Failed:"
    for f in "${errors[@]}"; do
        echo "  - $f"
    done
    exit 1
fi
