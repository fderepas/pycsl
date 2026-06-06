# Module6_WhyMLTranspiler ↔ Formal-Semantics Lemma Mapping

**Status:** ⚠️ **Historical document.** The `#@ proof rocq:` / `#@ proof lean:` proof-attribution directives this mapping was designed around were swept on 2026-05-27 (see `proof-to-axiom-from.md`). The text below is preserved as historical context.

Generated as part of `plan-formal-05.md` Layer 4 rollout. Module6 is
the largest and most semantically dense PyCSL module: 3508 lines,
~150+ methods, including the WP-rule statement handlers
(`_handle_*_stmt`) that map 1:1 to arms of the `wp` fixpoint in
`Phase4_WP.v` / `WP.lean`.

**Lemma family**: WP calculus implementation and soundness.

- Rocq: `wp` (fixpoint in `Phase4_WP.v`), `pycsl_soundness` (theorem
  in `Phase5b_Soundness.v`), `while_inv_preserved` (lemma in
  `Phase5a_WhileInv.v`), `wp_mono`, `lift_continue_wp`,
  `wp_aug_assign_for_idx`, `ghost_stmt_preserves_reg_state`.
- Lean: `wp` (def in `WP.lean`), `pycsl_soundness` (theorem in
  `Soundness.lean`), `while_inv_preserved` (in `WhileInv.lean`),
  `wp_mono`.

**Naming convention**: qualnames use `Pycsl.Reference.Module6.<lemma>`.
Rocq uses snake_case throughout; Lean's `wp` / `pycsl_soundness` /
`while_inv_preserved` / `wp_mono` are also snake_case in this module's
files (unusual for Lean — but matches the actual file content).

## Statement-handler methods (most numerous)

Each `_handle_<construct>_stmt` Python method implements one arm of
the `wp` fixpoint. The umbrella attribution cites the fixpoint
itself (since the per-arm soundness is built into how the fixpoint
is defined — there's no separate per-arm theorem in Phase4_WP.v).

| Python method | Rocq lemma | Lean lemma | Notes |
|---|---|---|---|
| `_handle_assign_stmt` | `wp` + `handle_assign_branches_correct` (Phase6e_HandleAssignEnglish.v) | `wp` + `handleAssignBranchesCorrect` (HandleAssignEnglish.lean) | basic assignment + 3-branch dispatch refinement from english-01.md |
| `_handle_augassign_stmt` | `wp_aug_assign_for_idx` | `wp_mono` | bounded augassign correctness |
| `_handle_while_stmt` | `while_inv_preserved` | `while_inv_preserved` | loop invariants |
| `_handle_for_stmt` | `while_inv_preserved` | `while_inv_preserved` | for→while desugar then loop |
| `_handle_if_stmt` | `wp` (`SIf` arm) | `wp` (`.if` arm) | conditional WP |
| `_handle_array_set_stmt` | `wp` (`SArraySet` arm) | `wp` (`.arraySet` arm) | array update |
| `_handle_return_stmt` | `wp` (`SReturn` arm) | `wp` (`.return` arm) | return-exception encoding |
| `_handle_try_stmt` | `wp` (`STryCatch` arm) | `wp` (`.tryCatch` arm) | exception handler |
| `_handle_ghost_assign_stmt` | `ghost_stmt_preserves_reg_state` | `wp_mono` | ghost-state preservation |
| `_handle_ghost_array_set_stmt` | `ghost_stmt_preserves_reg_state` | `wp_mono` | ghost-array update |
| `_handle_fieldassign_stmt` | `wp` (`SAssign` arm, with field-resolution) | `wp` | field write |
| `_handle_fieldaugassign_stmt` | `wp_aug_assign_for_idx` | `wp_mono` | field augassign |
| `_handle_critical_section_stmt` | `wp` (`SCritical` arm) | `wp` (`.critical` arm) | mutex acquisition |
| `_handle_tuple_unpack_stmt` | `wp` (`STupleUnpack` arm) | `wp` | tuple binding |

## Top-level transpile entry

| Python method | Rocq lemma | Lean lemma | Notes |
|---|---|---|---|
| `transpile` | `pycsl_soundness` | `pycsl_soundness` | the whole-program soundness theorem |

## Expression handlers (umbrella)

The `_handle_*_expr` family (~50 methods) all participate in
generating WP-correct VC text for contract expressions. They share
the `wp` / `wp_mono` attribution at the umbrella level — each is a
small lookup or string-build, not its own theorem.

| Python method (umbrella) | Rocq lemma | Lean lemma | Notes |
|---|---|---|---|
| `_handle_binop` (representative of all `_handle_*_expr`) | `wp_mono` | `wp_mono` | expression-side VC building preserves WP monotonicity |

## Coverage gaps (no `#@ proof` line emitted)

- All `_emit_preamble_*` methods (`_emit_preamble_uses`,
  `_emit_preamble_exceptions`, `_emit_preamble_helpers`,
  `_emit_preamble`, `_emit_shared_state`, `_emit_type_decls`) —
  pure WhyML scaffolding (declarations, `use` imports, exception
  types). No semantic content beyond syntax.
- `_emit_frame_condition`, `_build_witness_str`, `_build_param_list`,
  `_emit_contracts`, `_emit_body_code`, `_emit_function` — code-gen
  scaffolding that calls the `_handle_*_stmt` family. Inherit the
  umbrella attribution at `transpile`.
- Sub-call helpers (`_handle_len_call`, `_handle_join_call`,
  `_handle_sum_call`, `_handle_dotted_call`) — builtins. No formal
  theorem; covered by `eval_expr_translate_runtime` in Module5's
  expression-translation attribution.
- All `__init__` constructors.
- Per-expression-form helpers (`_handle_old_expr`, `_handle_at_expr`,
  `_handle_arraylen_expr`, `_handle_lambda_expr`, etc.) — leaf
  string-builders.

## Verification

```bash
for thm in wp pycsl_soundness while_inv_preserved wp_mono wp_aug_assign_for_idx \
           lift_continue_wp ghost_stmt_preserves_reg_state; do
    grep -l "Lemma $thm\b\|Theorem $thm\b\|Fixpoint $thm\b" src/formal-semantics/rocq/*.v \
      > /dev/null || echo "MISSING ROCQ: $thm"
done

for thm in wp pycsl_soundness while_inv_preserved wp_mono; do
    grep -l "theorem $thm\b\|def $thm\b" src/formal-semantics/lean/PyCSL/*.lean \
      > /dev/null || echo "MISSING LEAN: $thm"
done
```
