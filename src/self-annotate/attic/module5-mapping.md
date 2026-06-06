# Module5_IREmitter ↔ Formal-Semantics Lemma Mapping

**Status:** ⚠️ **Historical document.** The `#@ proof rocq:` / `#@ proof lean:` proof-attribution directives this mapping was designed around were swept on 2026-05-27 (see `proof-to-axiom-from.md`). The text below is preserved as historical context.

Generated for `tuesday-02.md` pilot. Each row maps a Python method in
`src/self-annotate/src/Module5_IREmitter.py` to its corresponding
machine-checked lemma in `src/formal-semantics/{rocq,lean}/`.

**Naming convention**: Rocq uses `wp_gen_<construct>` (snake_case);
Lean uses `wpGen_<construct>` (camelCase). The `#@ proof rocq:` /
`#@ proof lean:` directive qualnames match the actual file casing —
e.g. `#@ proof rocq: Pycsl.Reference.Module5.wp_gen_assign` and
`#@ proof lean: Pycsl.Reference.Module5.wpGen_assign`.

**Coverage**: only statement-level WP-correspondence lemmas
(`wp_gen_*` family) and the expression-translation lemma are mapped.
Helper / scaffolding methods (`_csl_*` contract-side emission,
`_fresh_var`, `visit_Module`, etc.) have no direct lemma and keep
trivial stubs.

## Statement-emission methods

| Python method | Rocq lemma | Lean lemma | Source file (Rocq / Lean) |
|---|---|---|---|
| `_py_stmt_assign` | `wp_gen_assign` | `wpGen_assign` | Phase6e_Corr_Simple.v / CorrSimple.lean |
| `_py_stmt_augassign` | `wp_gen_aug_assign` | `wpGen_augAssign` | Phase6e / CorrSimple |
| `_py_stmt_return` | `wp_gen_return` | `wpGen_return` | Phase6e / CorrSimple |
| `_py_stmt_while` | `wp_gen_while` | `wpGen_while` | Phase6f_Corr_Loops.v / CorrLoops.lean |
| `_py_stmt_for` | `wp_gen_for` | `wpGen_for` | Phase6f / CorrLoops |
| `_py_stmt_if` | `wp_gen_if` | `wpGen_if` | Phase6f / CorrLoops |
| `_py_stmt_continue` | `wp_gen_continue` | `wpGen_continue` | Phase6e / CorrSimple |
| `_py_stmt_break` | `wp_gen_break` | `wpGen_break` | Phase6e / CorrSimple |
| `_py_stmt_assert` | `wp_gen_assert` | `wpGen_assert` | Phase6e / CorrSimple |
| `_py_stmt_raise` | `wp_gen_raise` | `wpGen_raise` | Phase6e / CorrSimple |
| `_py_stmt_pass` | `wp_gen_skip` | `wpGen_skip` | Phase6e / CorrSimple |
| `_py_stmt_try` | `wp_gen_trycatch` | `wpGen_tryCatch` | Phase6g_Corr_Exc.v / CorrExc.lean |
| `_py_stmt_annassign` | `wp_gen_assign` | `wpGen_assign` | Phase6e / CorrSimple — annotated assign reduces to plain assign |
| `_py_stmt_with` | `wp_gen_critical` | `wpGen_critical` | Phase6f / CorrLoops — context manager ≈ critical section |
| `_py_stmts_to_ir` | `wp_gen_seq` | `wpGen_seq` | Phase6f / CorrLoops — sequencing |

## Expression-emission methods

A single soundness lemma covers all expression-level emission. The
expression-helper methods (`_py_expr_to_ir`, `_py_expr_binop`,
`_py_expr_compare`, …) share this attribution.

| Python method | Rocq lemma | Lean lemma | Source file |
|---|---|---|---|
| `_py_expr_to_ir` (umbrella) | `eval_expr_translate_runtime` | `vcgSound` | Phase6c_ExprTrans.v / Why3Vcg.lean |
| `_py_expr_unaryop` | `eval_expr_translate_runtime` | `vcgSound` | same |
| `_py_expr_binop` | `eval_expr_translate_runtime` | `vcgSound` | same |
| `_py_expr_compare` | `eval_c_translate` / `eval_bool_translate_runtime` | `vcgSound` | Phase6c / Why3Vcg |
| `_py_expr_boolop` | `eval_bool_translate_runtime` | `vcgSound` | Phase6c / Why3Vcg |

## Coverage gaps (no `#@ proof` line emitted)

These methods have no 1:1 formal-semantics lemma. They keep the
trivial `#@ requires 1 == 1` / `#@ ensures 1 == 1` stub. Fabricating
a theorem name would silently corrupt the trust chain.

- `__init__`, `visit_Module`, `visit_ClassDef`, `visit_FunctionDef` — top-level scaffolding.
- `_get_mutex_invariant_ir`, `_fresh_var` — internal helpers.
- `_csl_*` (all ~60 contract-side IR emitters) — these emit *contract* IR, not statement IR. The formal semantics treats contracts via `ContractExpr` in `Phase1_AST.v`, but no per-helper soundness lemma exists.
- `_py_expr_name`, `_py_expr_constant`, `_py_expr_tuple`, `_py_expr_subscript`, `_py_expr_list`, `_py_expr_attribute`, `_py_expr_dict`, `_py_expr_set`, `_py_expr_*comp`, `_py_expr_fstring`, `_py_expr_ifexp`, `_py_expr_starred`, `_py_expr_walrus`, `_py_expr_lambda`, `_py_expr_slice` — sub-cases of `_py_expr_to_ir`. Aggregated under the `_py_expr_to_ir` attribution above; individual methods omit the `#@ proof` line to avoid duplicate citations.
- `_py_op_to_str`, `_py_stmt_delete`, `_py_stmt_match`, `_py_stmt_expr`, `_csl_list_to_ir`, `_comprehension_generators_to_ir`, `_process_while`, `_process_for`, `_process_if`, `_match_pattern_to_ir`, `_scan_2d_in_*`, `_collect_2d_params`, `_collect_class_fields`, `_should_skip_method`, `_build_function_ir`, `_detect_purity`, `_detect_array_dimensions`, `generate_json` — algorithmic helpers with no semantic correspondence.

## Verification

```bash
# Confirm each cited Rocq lemma exists.
for thm in wp_gen_assign wp_gen_aug_assign wp_gen_return wp_gen_while \
           wp_gen_for wp_gen_if wp_gen_continue wp_gen_break wp_gen_assert \
           wp_gen_raise wp_gen_skip wp_gen_trycatch wp_gen_critical \
           wp_gen_seq eval_expr_translate_runtime eval_c_translate \
           eval_bool_translate_runtime; do
    grep -l "Lemma $thm" src/formal-semantics/rocq/*.v >/dev/null \
      || echo "MISSING ROCQ: $thm"
done

# Confirm each cited Lean theorem exists.
for thm in wpGen_assign wpGen_augAssign wpGen_return wpGen_while \
           wpGen_for wpGen_if wpGen_continue wpGen_break wpGen_assert \
           wpGen_raise wpGen_skip wpGen_tryCatch wpGen_critical \
           wpGen_seq vcgSound; do
    grep -l "theorem $thm" src/formal-semantics/lean/PyCSL/*.lean >/dev/null \
      || echo "MISSING LEAN: $thm"
done
```
