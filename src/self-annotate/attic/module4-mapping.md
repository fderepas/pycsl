# Module4_SemanticAnalyzer ↔ Formal-Semantics Lemma Mapping

**Status:** ⚠️ **Historical document.** The `#@ proof rocq:` / `#@ proof lean:` proof-attribution directives this mapping was designed around were swept on 2026-05-27 (see `proof-to-axiom-from.md`). The text below is preserved as historical context.

Generated as part of `plan-formal-05.md` Layer 4 rollout. Each row
maps a Python method in `src/self-annotate/src/Module4_SemanticAnalyzer.py`
to its corresponding machine-checked lemma / definition in
`src/formal-semantics/{rocq,lean}/`.

**Lemma family**: well-formedness. Module4's job is to build the
typing context Γ and verify that every contract expression is
`wf_expr Γ`-derivable. The formal-semantics correspondents:

- Rocq: `wf_expr` (inductive in `Phase1_AST.v`),
  `wf_expr_safe` (theorem in `Phase5b_Soundness.v`),
  `pycsl_soundness` (top-level theorem in `Phase5b_Soundness.v`).
- Lean: `WfExpr` (inductive in `AST.lean`),
  `wfExprSafe` (theorem in `Soundness.lean`),
  `pycsl_soundness` (theorem in `Soundness.lean`).

**Naming convention**: qualnames use `Pycsl.Reference.Module4.<lemma>`.
Rocq uses snake_case (`wf_expr`, `wf_expr_safe`); Lean mostly uses
CamelCase for inductives (`WfExpr`) and snake_case for the headline
theorem (`pycsl_soundness`) — directives match each file's casing.

## Methods with formal correspondence

| Python method | Rocq lemma | Lean lemma | Source file |
|---|---|---|---|
| `_validate_contract` | `wf_expr` (inductive) | `WfExpr` (inductive) | Phase1_AST.v / AST.lean |
| `_validate_function_contracts` | `wf_expr_safe` | `wfExprSafe` | Phase5b_Soundness.v / Soundness.lean |
| `_build_function_scope` | `wf_expr` (Γ construction) | `WfExpr` (context construction) | Phase1_AST.v / AST.lean |
| `process` (top-level entry) | `pycsl_soundness` | `pycsl_soundness` | Phase5b_Soundness.v / Soundness.lean |

## Coverage gaps (no `#@ proof` line emitted)

These methods have no 1:1 formal lemma. They keep structural
contracts only.

- `_iter_csl_children`, `extract_variables`, `contains_result`, `_get_type_name` — pure helpers / tree walkers.
- `_validate_proj_indices`, `_validate_predicate_bases` — sub-cases of `_validate_contract` (subsumed by `wf_expr` at the call site).
- `_extract_held_mutexes`, `_check_protected_*`, `_validate_mutex_invariant_scope`, `_check_shared_access`, `_check_expr_for_shared`, `_protected_*` — concurrency analysis. The formal semantics has `wp_gen_critical` (Phase6f) but no `wf_*` lemma covering shared-variable access discipline yet. Gap documented; future formal work could close it.
- `visit_Module`, `visit_ClassDef`, `_collect_class_field_types`, `visit_FunctionDef`, `visit_While` — `ast.NodeVisitor` scaffold; cites methods are the per-construct validators.
- `_validate_assigns_regions`, `_validate_subscript_assignments` — frame-condition / bounds checks. No direct lemma (Phase6 lemmas about IR-emission, not pre-emission checks).
- `__init__` — constructor.

## Verification

```bash
# Confirm each cited Rocq lemma exists.
for thm in wf_expr wf_expr_safe pycsl_soundness; do
    grep -l "Lemma $thm\|Theorem $thm\|Inductive $thm" src/formal-semantics/rocq/*.v \
      > /dev/null || echo "MISSING ROCQ: $thm"
done

# Confirm each cited Lean theorem/inductive exists.
for thm in WfExpr wfExprSafe pycsl_soundness; do
    grep -l "theorem $thm\|inductive $thm" src/formal-semantics/lean/PyCSL/*.lean \
      > /dev/null || echo "MISSING LEAN: $thm"
done
```
