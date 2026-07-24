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
# B1 (b1-plan.md §8/B1.3): resolve cross-tree imports (notably the mirror's
# `from ir_schema import AssignStmt, …`) against the real typed dataclasses in
# src/pycsl/, so imported IR types are records with typed fields instead of
# opaque stubs. Opt-in, searched after the built-in roots — regression-free
# (verdicts identical with/without; verified across the suite).
IMPORT_PATH="--import-path $PROJECT_ROOT/src/pycsl"

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
    # Wall-plan v2 Phase 1 (deliverable 4): the typed IR-node accessor layer, fully
    # verified (no \trusted) — total, exception-free string-read + guard accessors.
    "src/self-annotate/src/module6_whyml/irx.py"
    "src/self-annotate/src/__init__.py"
    "src/self-annotate/src/module6_whyml/__init__.py"
    # Bucket C — research-grade, \trusted reviewer with stub bodies
    # class-variant-impl.md (self-tcb-reduction item 3): emit_why3.py holds the
    # first class-instance-variant conversion (`contains_unsupported` over the
    # `term` ADT) — add it to the FULL-FILE proof gate (lesson 10) so the whole
    # file (converted stub + its `type term` theory + the still-`\trusted` `_pp`)
    # is proven together, not just `--fun`.
    "src/self-annotate/src/proof2why3/emit_why3.py"
    # class-variant-impl.md §OUTCOME-TL (self-tcb-reduction item 3): proof2why3/ir.py
    # holds the T-set/list LEAF conversions (`mk_arrow_chain` list-fold builder,
    # `flatten_arrow_chain` while-spine tuple return, `free_vars` set-fold) over the
    # `term` variant — add it to the FULL-FILE proof gate (lesson 10) so the whole
    # file (converted leaves + `type term` theory + the still-`\trusted` pp vals) is
    # proven together, not just `--fun`.
    "src/self-annotate/src/proof2why3/ir.py"
    "src/self-annotate/src/audit_proof.py"
    "src/self-annotate/src/Module6_WhyMLTranspiler.py"
    "src/self-annotate/src/pycsl.py"
    "src/self-annotate/src/module6_whyml/auto_trust.py"
    "src/self-annotate/src/module6_whyml/expressions.py"
    "src/self-annotate/src/module6_whyml/statements.py"
    "src/self-annotate/src/module6_whyml/stmt_control_flow.py"
    "src/self-annotate/src/module6_whyml/preamble.py"
    # Bucket D — frontend/ mirror (relocated from top-level by 0f0f32c7; each mirrors a
    # live src/pycsl/frontend/ module and is a genuine full-file verification target).
    # The suite array was NOT updated at relocation time, so these silently left the gate;
    # repointed + completed here. Module4_SemanticAnalyzer was DELETED in the refactor
    # and REPLACED by core_ir_semantic.py — now gated (it holds verified conversions:
    # _hp_collect_written, _sa_walk via the traversal catamorphism generator).
    "src/self-annotate/src/core_ir_semantic.py"
    "src/self-annotate/src/frontend/__init__.py"
    "src/self-annotate/src/frontend/Module1_Ingestor.py"
    "src/self-annotate/src/frontend/Module2_Parser.py"
    "src/self-annotate/src/frontend/Module3_Weaver.py"
    "src/self-annotate/src/frontend/Module5_IREmitter.py"
    "src/self-annotate/src/frontend/ConcurrencyChecker.py"
    "src/self-annotate/src/frontend/import_classifier.py"
    "src/self-annotate/src/frontend/exec_splice.py"
    "src/self-annotate/src/frontend/ir_inline.py"
    "src/self-annotate/src/frontend/ir_resolve.py"
    "src/self-annotate/src/frontend/module_collect.py"
    "src/self-annotate/src/frontend/monomorphize.py"
    "src/self-annotate/src/frontend/pure_ast.py"
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
    # B1.3: the cross-tree import path is for the self-annotate MIRROR only — it
    # bridges the mirror's `from ir_schema import …` to the real typed dataclasses.
    # Real src/pycsl/ files resolve their own directory already; adding it there is
    # redundant and can perturb resolution (e.g. errors.py), so scope it to mirror.
    case "$rel" in
        src/self-annotate/*) ip="$IMPORT_PATH" ;;
        *)                   ip="" ;;
    esac
    output=$($PYCSL "$path" $ip 2>&1)
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
