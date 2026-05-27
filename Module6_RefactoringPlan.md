# Module 6 WhyML Transpiler — Refactoring Plan

> A plan for splitting `src/pycsl/Module6_WhyMLTranspiler.py` (~4,678 lines, 1 main class with ~117 methods plus a nested `IRScanner` class with 29 static methods) into a cohesive `module6_whyml/` package while preserving the external contract defined in `pycsl-software-architecture` Section 2.

---

## 1. Motivation

Module 6 is currently a single file holding two classes, ~146 methods, and 25+ instance fields on the main transpiler. The size on its own is not the problem — but several signals from the system-design paradigms point in the same direction:

- **SRP** — the class has multiple independent reasons to change: adding a memory model touches preamble/shared-state emission; adding a CSL statement touches statement handlers; adding an expression node touches expression handlers; changing type inference touches the type/coercion helpers; changing the SCC ordering touches a graph algorithm. Five orthogonal axes of change sharing one file is the canonical SRP smell.
- **High cohesion / low coupling** — method-name clusters reveal natural cohesion groups that already share signatures. Every `_handle_*_stmt` takes `(stmt, rest, local_refs, declared_refs, indent, in_loop)`. Every `_handle_*_expr` takes `(expr, local_refs, invariant_ctx, subst)`. The clusters are already there; the file boundary is what's missing.
- **KISS** — at 4,678 lines, the first action for any maintainer is a substring search. A smaller per-file surface reduces that tax.

The counterweights matter too:

- **YAGNI / Worse-Is-Better** — do not refactor for its own sake, and do not do everything at once. The `pycsl-reference` corpus gates each step. A working monolith beats an elegant refactor that breaks tests.
- **Composition vs. Simplicity** — there is a tempting wrong turn here: invent a `StatementHandler` / `ExpressionHandler` class hierarchy. That produces the "maze of tiny pieces" the paradigms skill warns about. Compose at meaningful boundaries (one file per cluster), not per-method.

The remainder of this document is the concrete plan that takes these tensions into account.

---

## 2. What already favours the split

The file is more refactor-ready than the line count suggests. Three pieces of pre-existing structure carry most of the weight:

**IRScanner is already pure and stateless.** Lines 7–538, 29 `@staticmethod` methods, zero `self.` references. It exists as a separate class today only conceptually — physically it sits inside `Module6_WhyMLTranspiler.py`. Extracting it is a cut-paste plus one import. There is no state to disentangle and no coupling to break.

**The `_EXPR_DISPATCH` table already exists** (lines 606–662), with 54 entries mapping IR type strings to handler method names. The hard organizational work for the expression cluster — making the entry contract explicit — is already done. Splitting the 52 `_handle_*_expr` methods into a separate module is mostly mechanical because they all share a uniform signature and dispatch is centralised.

**The `transpile()` body is already split into phases A–H** via comment dividers (lines 3391, 3412, 3509, 3758, 3803, 3883, 3915, 4541). Those phase boundaries are an implicit file plan written by hand; the refactor mostly turns them into physical files.

**`__init__` already groups state by lifetime** via comments (lines 550–577): "Per-function state — reset per function via `_reset_function_state`" covers 14 fields; "Whole-module state — populated by `transpile()`" covers 7 fields. These are two implicit dataclasses waiting to be named.

The SRP argument from the analysis above still holds, but the *cost* of acting on it is much lower than the raw line count implies, because each of these four pieces of pre-existing structure removes ambiguity about where things should go.

---

## 3. Target layout

The external contract is fixed by `pycsl-software-architecture` Section 2: callers must continue to do `Module6_WhyMLTranspiler(json_ir, memory_model).transpile()` from `_run_pipeline()`. So Module 6 stays one module to the rest of the pipeline. The split is purely internal: a `Module6_WhyMLTranspiler.py` facade plus a `module6_whyml/` subpackage.

### 3.1 Facade

`src/pycsl/Module6_WhyMLTranspiler.py` keeps:

- The `Module6_WhyMLTranspiler` class declaration and `__init__`
- The class-level constants `_OP_MAP`, `_EXPR_DISPATCH`, `_WHYML_RESERVED`
- The `_heap_var` property
- The `transpile()` entry point — kept thin, the same shape it has today
- Mixin inheritance from the cluster modules below

External callers see no change.

### 3.2 Subpackage `src/pycsl/module6_whyml/`

| File | Contents | Approx. methods | Approx. lines |
|---|---|---|---|
| `ir_scanner.py` | `IRScanner` class (lifted verbatim) | 29 | ~530 |
| `expressions.py` | `_expr_to_whyml`, `_expr_to_whyml_string_ctx`, 52 `_handle_*_expr` methods, plus `_handle_binop`, `_handle_call_expr`, `_handle_subscript`, `_handle_attribute_expr`, `_handle_dotted_call`, `_handle_len_call`, `_handle_join_call`, `_handle_sum_call`, `_emit_membership`, `_emit_bitwise_or_power`, `_to_bool`, `_coerce_str_arg`, `_array_coerce_arg`, `_coerce_to_int`, `_match_pattern_cond` | ~65 | ~1,150 |
| `statements.py` | `_stmts_to_whyml`, the 16 `_handle_*_stmt` methods, `_emit_body_code`, `_emit_first_assign`, `_emit_array_local_reassign`, `_emit_new_ghost_ref`, `_emit_frame_condition`, `_wrap_body_with_return_catch`, `_classify_iterable` | ~25 | ~900 |
| `preamble.py` | `_scan_preamble_needs`, `_emit_preamble`, `_emit_preamble_uses`, `_emit_preamble_exceptions`, `_emit_preamble_helpers`, `_emit_preamble_axioms`, `_emit_shared_state`, `_emit_type_decls`, `_emit_opaque_class_aliases` | 9 | ~450 |
| `functions.py` | `_emit_function`, `_build_param_list`, `_emit_contracts`, `_compute_return_type`, `_reset_function_state`, `_param_type_str`, `_symtype_to_whyml`, `_build_method_return_type_map`, `_build_method_param_types_map`, `_collect_record_fields` | 10 | ~400 |
| `scc.py` | `_sort_functions_by_scc`, `_compute_sccs`, `_find_calls_in_ir` | 3 | ~150 |
| `auto_trust.py` | `_should_auto_trust_array_return`, `_should_auto_trust_map_return`, `_should_auto_trust_tuple_return`, `_should_auto_trust_set_op`, `_collect_map_typed_locals`, `_has_set_op_on_map`, `_test_contains_map`, `_check_witness_vals`, `_build_witness_str`, `_is_linear_expr`, `_is_linear_vc` | 11 | ~300 |
| `types.py` | `_field_type_for`, `_field_type_of`, `_resolve_effective_ghost_type`, `_rhs_yields_array`, `_rhs_yields_map`, `_val_is_bool`, `_first_assign_kind`, `_track_collection_metadata`, `_collect_array_var_assigns`, `_collect_dict_var_assigns`, `_bool_ir_to_int_wrap` | 11 | ~250 |
| `abstract_ops.py` | `_add_abstract_op`, `_find_abstract_val_insert_idx`, `_insert_abstract_val_block` | 3 | ~50 |
| `identifiers.py` | `_whyml_ident`, `_safe_mutex_name`, `_op` (and re-exports of `_OP_MAP`, `_WHYML_RESERVED` if helpful) | 3 | ~40 |

`ir_scanner.py`, `scc.py`, `auto_trust.py`, and `identifiers.py` are essentially independent. The others share state with the facade and therefore couple to it via mixin inheritance (see §5).

### 3.3 Why these boundaries

Each file answers one "reason to change":

- `ir_scanner.py` — "I need a new piece of IR-tree analysis." Pure analysis. No emission.
- `expressions.py` — "I want to support a new expression node." Adding a row to `_EXPR_DISPATCH` and a handler function.
- `statements.py` — "I want to support a new statement form." Adding a case (or dispatch entry — see §4.2) and a handler function.
- `preamble.py` — "I want a new `use` or helper emitted at the top." All preamble feature-flag logic lives in one place.
- `functions.py` — "I want to change how a function block is assembled." Contracts, parameter lists, return-type computation, frame conditions.
- `scc.py` — "I want to change the function emission order or recursion detection." Pure graph algorithm.
- `auto_trust.py` — "I want to change when a function becomes `val` instead of `let`." Bounded, self-contained.
- `types.py` — "I want to change type inference for assignments or return types."
- `abstract_ops.py` — "I want to change how abstract `val` declarations are emitted."
- `identifiers.py` — "I want to change how Python names map to WhyML identifiers."

These match cleanly onto the existing Phase A–H comments in `transpile()`.

---

## 4. Two architectural cleanups worth pairing with the split

Two cleanups are *not* required to split files, but are natural to consider during the work. Both are flagged here so the decision is deliberate rather than implicit.

### 4.1 Extract `FunctionContext` and `ModuleContext` dataclasses

The 25+ instance fields on `Module6_WhyMLTranspiler` collapse to two natural groupings, already labelled by your own comments:

- **`FunctionContext`** (14 fields) — `_bounded_int`, `_array2d_params`, `_current_array1d_params`, `_current_params`, `_current_symbol_table`, `_array_locals`, `_dict_locals`, `_record_locals`, `_lambda_locals`, `_current_self_type`, `_func_return_type`, `_current_tuple_arity`, `_has_early_ret`, `_for_idx_init`. All reset by `_reset_function_state`.
- **`ModuleContext`** (7 fields) — `_all_record_fields`, `_module_func_names`, `_module_method_return_types`, `_module_method_param_types`, `_auto_trusted_array_returns`, `_auto_trusted_tuple_returns`, `_auto_trusted_map_returns`, `_auto_trusted_set_op`. Populated by `transpile()` before any function emission.

After the extraction, `Module6_WhyMLTranspiler` shrinks from 25+ flat attributes to roughly `self.module_ctx`, `self.func_ctx`, `self._abstract_ops`, `self._record_types`, `self._shared_var_names`, `self.ir`, `self.memory_model`. This is *Information Hiding* applied as the paradigms skill describes it — the caller can finally tell which fields are per-function vs per-module.

This is the only step in the plan that changes call-site shape (`self._current_params` → `self.func_ctx.current_params`), which is why it is sequenced last and done incrementally.

### 4.2 Replace the `_stmts_to_whyml` if/elif chain with a dispatch table

`_stmts_to_whyml` (lines 3158–3247) uses a 17-case `if/elif` chain on `s_type`. The expression side already migrated to `_EXPR_DISPATCH`; doing the same for statements gives three benefits:

1. Symmetry with the expression cluster (one pattern across both files).
2. Adding a new statement type becomes one dict entry plus one function, matching the "Adding a new CSL keyword" workflow in `pycsl-software-architecture` Section 6.
3. `statements.py` can register its handlers the same way `expressions.py` does.

This can be done in the same PR as the `statements.py` split, or kept separate. Either is fine; the file split is cleaner without it, so the separate PR is mildly preferred.

---

## 5. Mechanical wiring: mixins

Most cluster methods need `self` for state access, so the simplest wiring is **mixin classes**:

```python
# expressions.py
class ExpressionEmissionMixin:
    def _expr_to_whyml(self, expr, local_refs, invariant_ctx=False, subst=None):
        ...
    def _handle_call_expr(self, expr, local_refs, invariant_ctx=False, subst=None):
        ...
    # etc.

# Module6_WhyMLTranspiler.py
from .module6_whyml.expressions import ExpressionEmissionMixin
from .module6_whyml.statements import StatementEmissionMixin
# ... etc.

class Module6_WhyMLTranspiler(
    ExpressionEmissionMixin,
    StatementEmissionMixin,
    PreambleMixin,
    FunctionEmissionMixin,
    SCCMixin,
    AutoTrustMixin,
    TypeInferenceMixin,
    AbstractOpsMixin,
    IdentifierMixin,
):
    def __init__(self, json_ir: str, memory_model: str = "hoare") -> None:
        ...
    def transpile(self) -> str:
        ...
```

Call sites do not change: `self._handle_assign_stmt(...)` continues to work, `__init__` stays where it is, and the reference corpus should stay green through every step.

The cost of mixins, honestly stated: **coupling stays invisible.** Any mixin can in principle reach into any attribute on `self`. The paradigms skill calls this out as the tension between *Encapsulation* and *Composition vs. Simplicity*. For this refactor the cheap, stays-green win is the right tradeoff — and §4.1 is the followup that makes coupling visible *if and when* the team chooses to invest.

For the four largely-independent clusters (`ir_scanner.py`, `scc.py`, `auto_trust.py`, `identifiers.py`), free functions are preferred over mixins where they work cleanly:

- `IRScanner` is already a class of static methods; ship it as-is.
- `_compute_sccs` and `_find_calls_in_ir` take their inputs as parameters today; turn them into module-level functions taking `(names, call_graph)` and `(obj, func_names_set)` directly.
- `_whyml_ident` and `_safe_mutex_name` are already `@staticmethod`; lift them to module-level.

---

## 6. Execution order (risk-ranked, with the corpus as the gate)

Each step is an independent PR. The `pycsl-reference` test corpus must pass after each PR before the next is started. This is the *Worse-Is-Better* discipline applied: ship working slices, do not chain risky steps.

| # | Step | Risk | What it touches | Test signal |
|---|---|---|---|---|
| 1 | Extract `IRScanner` → `module6_whyml/ir_scanner.py` | Trivial | Cut-paste, one `from .module6_whyml.ir_scanner import IRScanner` in the facade | Corpus + any unit tests on IRScanner |
| 2 | Extract `scc.py` and `identifiers.py` | Low | Free functions, no `self`, ~6 methods total | Corpus |
| 3 | Extract `auto_trust.py` as a mixin | Low–medium | 11 self-contained methods, internal vocabulary | Corpus |
| 4 | Extract `abstract_ops.py` as a mixin | Low | 3 methods, narrow surface | Corpus |
| 5 | Extract `types.py` as a mixin | Medium | 11 type-related methods, read-heavy on state | Corpus |
| 6 | Extract `expressions.py` as a mixin | Medium | The largest single move (~65 methods, ~1,150 lines). `_EXPR_DISPATCH` is the contract — verify each handler resolves to the new module via inheritance | Corpus |
| 7 | Extract `statements.py` as a mixin | Medium | 25 methods. **Do not also do §4.2 (statement dispatch table) in this PR.** | Corpus |
| 8 | Extract `preamble.py` and `functions.py` as mixins | Low–medium | What's left | Corpus |
| 9 | *(Optional)* §4.2 — statement dispatch table | Low | Pure refactor of `_stmts_to_whyml` body, no method moves | Corpus |
| 10 | *(Optional)* §4.1 — `FunctionContext` / `ModuleContext` dataclasses | High | Changes call sites; do one cluster at a time, run corpus between each | Corpus, ideally also targeted unit tests on extracted state |

Two rules of thumb across all steps:

- **Do not combine file moves with logic changes in the same PR.** Splitting files is mechanical; extracting state, or rewriting `_stmts_to_whyml` as a dispatch table, is design. Mixing them turns a green-bar refactor into a debugging session and erases the test-corpus gate.
- **Steps 1–4 are pure wins; step 10 is the only one with real risk.** It is sequenced last on purpose. If the team's appetite runs out after step 8, the file is already much better than today and step 10 can wait indefinitely without regret.

---

## 7. Updates to `pycsl-software-architecture` skill

The skill file must be updated as part of this work, or it will misdirect future agents using RAG retrieval against it.

### After step 1

`Section 1 — Repository layout` should describe Module 6 as a package, e.g.:

```text
Module6_WhyMLTranspiler.py  ← facade; JSON IR string → WhyML text
module6_whyml/
  ir_scanner.py             ← stateless IR-tree analysis
```

### After each subsequent step

Add the new file under `module6_whyml/` in the layout block with a one-line role description.

### After step 7

`Section 6 — How to extend the compiler and agents`, "Adding a new CSL keyword" step 6, currently reads:

> 6. `Module6_WhyMLTranspiler.py` — transpile it to the corresponding WhyML syntax.

It should become:

> 6. `module6_whyml/expressions.py` or `module6_whyml/statements.py` — add the handler function and register it in `_EXPR_DISPATCH` (expressions) or the statement dispatch table (statements).

This change is part of the same PR as step 7 (or step 9 if it lands), not deferred.

Per the skill file's footer, this is a Configuration Item under baseline BL-SYSDESIGN-001 — changes require Change Control Board approval per `cmmi-glue` Workflow 2. Plan the skill update as part of each step's PR description so the CCB sees the matched code/skill diff.

---

## 8. Anti-patterns to avoid during this work

Concrete failure modes the paradigms skill names, with the form they would take here:

- **Over-applying SRP** — splitting `expressions.py` further into one-handler-per-file. The unit of responsibility is "expression emission," not "one expression type."
- **Premature DRY** — noticing that many `_handle_*_expr` methods start with `args = [self._expr_to_whyml(a, ...) for a in expr["args"]]` and trying to factor that out into a base class. Two functions sharing a line today may diverge tomorrow; the dispatch-table pattern is the right level of abstraction.
- **Speculative composition** — inventing a `Handler` ABC with `register`/`dispatch`/`compose` methods. `_EXPR_DISPATCH` is a `dict`; that is sufficient and matches *KISS*.
- **Hidden coupling after mixin split** — assuming the file split alone has reduced coupling. It has not; it has reorganised it. The coupling becomes visible only after §4.1.
- **Big-bang refactor** — doing steps 1–10 in one branch. The corpus stops being a gate, every regression is harder to localise, and review becomes infeasible.

---

## 9. Out of scope for this plan

The following are real concerns but are not addressed here:

- Performance characteristics of the transpiler. None of the steps are expected to change observable performance; if they do, that is a regression, not a feature.
- The `_OP_MAP` and `_WHYML_RESERVED` constant tables. They are small, stable, and load with the class; moving them is a style choice not a correctness one.
- Whether `IRScanner` should be exposed as a public API. Currently it is consumed only by the transpiler. Promoting it to a public utility would be a separate design decision, made after step 1 if needed.
- The agent pipeline's reliance on Module 6's structure. Agents that retrieve Module 6 source via RAG will see different chunks after the split; if a downstream prompt depends on specific method co-location, that prompt may need updating. Audit `config/skills/` and `agents/` for any hard-coded references to the monolithic file before step 1 lands.

---

## 10. Summary

The refactor is justified by SRP and natural cohesion clusters that the file's own comments already mark. The cost is low because three pieces of pre-existing structure — `IRScanner` as a stateless class, `_EXPR_DISPATCH` as an explicit contract, and the Phase A–H comments in `transpile()` — have already done the organizational work. The recommended path is nine small PRs gated on the reference corpus, starting with the zero-risk `IRScanner` extraction and ending optionally with a `FunctionContext` / `ModuleContext` dataclass extraction. The architecture skill is updated in lockstep so future agents do not look in the wrong place.

The principle that governs the order is *Worse-Is-Better*: ship the cheap improvements first, treat the corpus as the gate, and stop whenever further work no longer pays for itself.
