# wall-plan-v3 Phase 0 — walker-shape census + placement + pattern spec (VERDICT: NO-GO on the majority gate)

**2026-07-07. Measurement/design only — no `src/pycsl` / mirror edits, ledger untouched, count 1248.**
Continues `wall-plan-v2-phase2c-plan.md` (§0 thesis, §4 Phase 0) and the phase2b/2c NO-GO. Reuses the
L1-certified `pydict` + the L2-proven target shapes (`v2_iter_mutate_spike.mlw`,
`v2_listdict_recurse_spike.mlw`).

---

## 0. Bottom line

- **Census gate: NO-GO.** Of **541** residual `\trusted` methods that read the compiler's
  `Dict[str,Any]` IR (across the 9 IR-consuming modules), the closed pattern-class
  **{T-A, T-B, accessor-only}** covers **131 (24.2%)**; **out-of-pattern dominates at 410 (75.8%)** — a
  clear majority. The plan's thesis ("the residual is a closed catamorphism class") does **not** cover a
  worthwhile majority. Per the §4 gate ("if T-A+T-B+accessor-only cover ≪ the residual → the closed-class
  thesis fails"), this is the **decisive NO-GO**.
- **BUT a real refinement over phase2c:** the **T-A generic-walk template family is 22 methods, not 2.**
  Phase2c censused only `module6_whyml` and found 2 (`find_named_expr_targets`, `_collect_assign_targets`).
  The migrated Module-4 semantic checks in **`core_ir_semantic.py`** and the IR-resolution passes are
  *pervasively* the exact T-A shape (`_sa_walk`, `_cp_walk`, `_gso_walk`, `_pb_descend`, `_cs_descend`,
  `_collect_call_targets`, `_ir_free_vars`, `find_calls_in_ir`, `_walk_dicts`, …). So the T-A template, **if
  built, is materially more valuable than phase2c implied** (≈22-method conversion from one template) — even
  though it is a *minority* of the residual.
- **Placement: FEASIBLE, but the plan's stated location is obsolete.** `Module4_SemanticAnalyzer` was
  **dropped** (its checks migrated to run *on the IR*, i.e. **after** the tuple-target erasure). There is no
  longer a "semantic-analysis time" AST pass. The intact AST (tuple targets, `isinstance` narrowings) exists
  **only as Module 5's input** (`unified_ast`), and the erasure happens *inside* Module 5 at
  `frontend/Module5_IREmitter.py:1477`. A `GenericWalk` node **can** be recorded — but as an **AST pass
  within Module 5, before line 1477**, not as a separate pre-Module-5 semantic pass. Not a blocker; a
  relocation.

**Net Phase-0 verdict: NO-GO for the plan as written (closed-class ≠ majority).** A scoped, honest
alternative — *build only the T-A template for the ~22-method generic-walk family, and ledger the rest* — is
viable but is a **different, smaller** proposition than "the residual is a closed catamorphism class." See §5.

---

## 1. The walker-shape census (the make-or-break)

**Scope of "residual".** The L3 wall is about reading the compiler's `Dict[str,Any]` IR. Residual =
`\trusted` methods (marker `#@ \trusted reviewer: pycsl-self-annotate`, **1228** total in the mirror
`src/self-annotate/src/`) whose **live** `src/pycsl` body structurally reads an IR/dict param
(`.items()`/`.values()`/`.get(k)`/`d[k]`/self-recursion), **restricted to the 9 IR-consuming modules**:
`core_ir_semantic.py`, `Module6_WhyMLTranspiler.py`, `module6_whyml/*`, `frontend/Module5_IREmitter.py`,
`frontend/ir_resolve.py`, `frontend/ir_inline.py`, `frontend/monomorphize.py`,
`frontend/module_collect.py`, `frontend/exec_splice.py`.
**Excluded** (trusted for *unrelated* reasons — different datatypes, not the `Dict[str,Any]` IR):
`proof2why3/*` (its own sexp/Lean ADT), `frontend/pure_ast.py` (Python-AST unparser),
`Module1/Module2/Module3`, `ConcurrencyChecker` (text/AST, pre-IR), `audit_proof*`, `pycsl.py` CLI,
`ir_schema`, `exception_model`, `identifiers`. Method: `scratchpad/census_v3.py` (AST classifier) +
by-hand verification of every T-A/T-B candidate and a spot-check of the accessor/out boundaries.

### Coverage table

| bucket | n | % of residual | meaning |
|---|--:|--:|---|
| **T-A** (generic-walk + mutate) | **22** | 4.1% | `isinstance(dict/list); for v in obj.values()/items(): self(v)` catamorphism — the `v2_iter_mutate_spike` shape |
| **T-B** (read + build doc) | **3** | 0.6% | recursion over `List[dict]`/nested reading literal keys, builds a string — the `v2_listdict_recurse_spike` shape |
| **accessor-only** (strict) | **106** | 19.6% | small literal-key reader, no generic walk, no unbounded recursion — L1 routing *plausibly* suffices, no template |
| **out-of-pattern** | **410** | **75.8%** | not covered by the closed class |
| **RESIDUAL** | **541** | 100% | |

**Coverage `#(T-A+T-B+accessor-only)/#residual = 131/541 = 24.2%`.**
**Template-coverable `#(T-A+T-B)/#residual = 25/541 = 4.6%`.**
**Out-of-pattern = 75.8% (clear majority) ⇒ closed-class thesis FAILS the gate.**

Two honesty caveats that make 24.2% an **upper bound**, not a floor:
1. **accessor-only "coverage" is conditional.** It counts a method as covered iff *L1 routing alone*
   verifies it. That is asserted structurally (small, literal-key, scalar/str result, ≤4 emitter-helper
   fan-out), **not** proven per method. Several accessor methods still call other `\trusted` helpers or hit
   value-typing corners; some fraction of the 106 will *not* close on L1 routing alone.
2. The T-A/T-B templates only emit the *recursion skeleton*; a method whose **payload** calls another
   `\trusted` checker (`_pb_stmt`, `_typeddict_check_subscript`, `_stmt_is_noreturn_call`) is not *fully*
   verified until that helper is — so even the 25 template-coverable methods are "skeleton-coverable," not
   "conversion-guaranteed."

### T-A (n=22) — all verified genuine generic-walk catamorphisms

| file | method | class | LoC |
|---|---|---|--:|
| `core_ir_semantic.py` | `_collect_call_targets` | — | 13L |
| `core_ir_semantic.py` | `_pb_descend` | — | 9L |
| `core_ir_semantic.py` | `_pb_expr` | — | 57L |
| `core_ir_semantic.py` | `_cs_descend` | — | 9L |
| `core_ir_semantic.py` | `_ir_free_vars` | — | 45L |
| `core_ir_semantic.py` | `_sa_walk` | — | 22L |
| `core_ir_semantic.py` | `_cp_walk` | — | 12L |
| `core_ir_semantic.py` | `_gso_walk` | — | 17L |
| `core_ir_semantic.py` | `_hp_collect_written` | — | 11L |
| `core_ir_semantic.py` | `_conc_check_reads` | — | 10L |
| `core_ir_semantic.py` | `_typeddict_walk_subscripts` | — | 16L |
| `core_ir_semantic.py` | `_namedtuple_walk_construction` | — | 17L |
| `core_ir_semantic.py` | `_namedtuple_walk_subscripts` | — | 16L |
| `frontend/monomorphize.py` | `_scan_node_for_subscript_calls` | — | 30L |
| `frontend/ir_inline.py` | `_walk_dicts` | — | 8L |
| `frontend/ir_resolve.py` | `_collect_calls` | — | 11L |
| `module6_whyml/ir_scanner.py` | `find_named_expr_targets` | IRScanner | 10L |
| `module6_whyml/ir_scanner.py` | `collection_binder_kinds` | IRScanner | 17L |
| `module6_whyml/stmt_control_flow.py` | `_callee_raised_in` | ControlFlowStmtMixin | 39L |
| `module6_whyml/scc.py` | `find_calls_in_ir` | — | 11L |
| `module6_whyml/scc.py` | `find_self_method_calls` | — | 26L |
| `module6_whyml/functions.py` | `_collect_assign_targets` | FunctionEmissionMixin | 9L |

Deciding body feature (each verified against the live body): `if isinstance(x, dict): <pre-action reading
literal keys>; for v in x.values()/x.items(): <self>(v, acc) elif isinstance(x, list): for i in x:
<self>(i, acc)`. Sub-variants inside T-A (all catamorphic, but not *byte-identical* to the by-ref spike):
- **by-ref mutation** (`find_named_expr_targets`, `_collect_assign_targets`, `_hp_collect_written`) — exact
  spike shape.
- **functional fold** returning a `set`/`list` (`_ir_free_vars`, `_collect_calls`, `find_calls_in_ir`,
  `collection_binder_kinds`, `_scan_node_for_subscript_calls`) — `out |= self(v)`. A *second* template
  sub-form (accumulate-by-return), still structural, still provable, but the plan's single by-ref template
  does not emit it as-is.
- **check-walk** raising on violation (`_sa_walk`, `_cp_walk`, `_gso_walk`, `_pb_expr`, `_conc_check_reads`)
  — unit return, side-effect = `raise`. Payload is a literal-key test; well-typed/framed/terminating.
- **generator** (`_walk_dicts`, `yield from`) — a `yield`-based walk; recursion-template does not cover
  generators (a separate emitter concern). 1 method.

### T-B (n=3) — hand-curated (`v2_listdict_recurse_spike` shape)

| file | method | class | LoC |
|---|---|---|--:|
| `module6_whyml/expressions.py` | `_match_pattern_cond` | ExpressionEmissionMixin | 15L |
| `module6_whyml/ir_scanner.py` | `find_return_type` | IRScanner | 50L |
| `module6_whyml/stmt_control_flow.py` | `_render_match_pattern` | ControlFlowStmtMixin | 23L |

Deciding feature: structural self-recursion over nested `dict`/`List[dict]` reading **literal** keys and
building a **string** result. `find_return_type` is the frozen benchmark item 2.

### accessor-only (n=106) — by file (strict: L1 routing plausibly suffices, no template)

| file | n | | file | n |
|---|--:|---|---|--:|
| `module6_whyml/expr_ghost_collections.py` | 24 | | `module6_whyml/auto_trust.py` | 5 |
| `core_ir_semantic.py` | 18 | | `module6_whyml/types.py` | 5 |
| `frontend/Module5_IREmitter.py` | 14 | | `module6_whyml/stmt_control_flow.py` | 3 |
| `module6_whyml/expr_ghost_spec_ops.py` | 10 | | `frontend/ir_inline.py`, `frontend/exec_splice.py`, `module6_whyml/statements.py`, `module6_whyml/functions.py` | 2 each |
| `module6_whyml/expressions.py` | 9 | | `frontend/module_collect.py`, `module6_whyml/identifiers.py`, `module6_whyml/scc.py` | 1 each |
| `frontend/monomorphize.py` | 7 | | | |

Representative verified accessors: `_callable_tag_to_whyml` (tag→WhyML type map, 16L, scalar/str result);
`_emit_bitwise_or_power` (literal-key reads + constant fold, 24L); the `expr_ghost_collections`
`_handle_map_get_expr`/`_handle_set_add_expr` family (2–10L ghost-op emitters). Blocker = IR value-typing
(`Dict[str,Any]` int-collapse), which L1 routing addresses — **no** generic walk, **no** unbounded recursion.

### out-of-pattern (n=410) — grouped by primary disqualifier

| n | primary disqualifier |
|--:|---|
| 236 | reads literal keys but **builds/mutates a collection** (needs *collection-result modeling* — a separate unbuilt feature, neither template nor L1 routing) |
| 51 | uncategorized mixed IR readers (multi-blocker) |
| 33 | **generic `.items()`/`.values()` walk but NO self-recursion** (non-structural — no catamorphism to derive) |
| 23 | **structural literal-key recursion building a COLLECTION** (e.g. `find_ghost_vars`, `find_assigned_vars`) — recurses into fixed keys (`body`/`orelse`/`cases`), builds a `set`/`list`; **a third catamorphic family the two templates do not cover** |
| 20 | reads literal keys but **large/high-fanout** emitter method (trusted for orthogonal reasons: string ops, complex emission; L1 routing alone does not suffice) |
| 16 | **recursive PREDICATE** over IR (returns `bool`; e.g. `_is_string_expr`) — neither walk-mutate nor doc-fold |
| 9 | **early-return-in-loop** scan (worklist) |
| 6 | **generic-walk BUT subject mutation** during iteration (real disqualifier — matches `nearmiss_mutate`) |
| 5 | structural literal-key check-walk / dispatcher (unit-return, no build) |
| 4 | **emitter-core dispatcher** — self-recursion fanning out to many `_handle_*` (the 3 TCB giants: `_stmts_to_whyml`, `_expr_to_whyml`, `_expr_to_whyml_string_ctx`) |
| 4 | **generic-walk BUT break/early-return in loop** (real disqualifier — matches `nearmiss_break`) |
| 2 | `while`-loop worklist |
| 1 | self-recursion, non-generic-walk, non-doc-build |

**Reading of the out-of-pattern majority:** the single biggest bucket (236 + 23 = 259) is *collection-result
building* — methods that read IR by literal keys and construct a `list`/`dict`/`set`/string result. These are
neither the T-A (walk-and-mutate-a-set) nor T-B (doc-string-fold) shape. They would need a **collection-
result modeling** feature that is *orthogonal to the L3 generic-walk synthesis subsystem*. That, plus the 33
non-self generic walks and the 16 recursive predicates, is why the closed class misses three-quarters of the
residual.

---

## 2. Placement check (§3.3-3 / T1)

**Exact erasure location — confirmed:** `src/pycsl/frontend/Module5_IREmitter.py:1477`, in `_process_for`:

```python
target = node.target.id if isinstance(node.target, ast.Name) else "_for_target"
```

A tuple `for`-target (`for k, v in …`, `node.target` an `ast.Tuple`) is **not** `ast.Name`, so it collapses
to the opaque literal `"_for_target"`; `k`/`v` are never bound. This erasure is at **IR-construction** time.

**Pipeline order (verified in `src/pycsl/pycsl.py`):**
`Module1_Ingestor → Module2_Parser → Module3_Weaver (⟶ unified_ast) → Module5_IREmitter(unified_ast) ⟶
json_ir → validate_ir → run_ir_semantic_checks(ir_data) → ir_resolve → Module6`.

**Key architectural finding — the plan's "semantic-analysis time" is obsolete.**
`pycsl.py:21`: *"Module 4 (SemanticAnalyzer) DROPPED — B-final reorder: its checks migrated to the IR"*.
There is **no** AST-level semantic-analysis pass anymore; `run_ir_semantic_checks` runs on the **IR** — i.e.
**after** the line-1477 erasure. So the plan's T1 ("recognize at semantic-analysis time where tuple targets
are intact") points at a stage that no longer exists.

**Can the `GenericWalk` node be recorded before the erasure? — YES, with relocation.**
The intact AST (tuple targets, `isinstance` narrowings, the self-call structure) is fully present in
`unified_ast`, which is exactly **Module 5's input**. The erasure happens *inside* Module 5, at line 1477.
Therefore a recognizer can run as an **AST pass at Module-5 entry** (over `unified_ast`, or equivalently as a
Module-3/Module-5 boundary pass), recording `GenericWalk {subject, key_filter, pre_action, recursion_sites,
accumulator}` **before** `_process_for` erases the tuple target. Not a placement blocker.

Moreover, for the **T-A** shape the tuple binding is *recoverable even after erasure*: the pattern keys on
the `.items()`/`.values()` call plus self-recursion on the value; the loop variable `k` is used only in the
literal-key skip-guard (`if k == "stmt": continue`), which lowers to skipping the `K_stmt` cons-cell in the
`walk_dict` spine. So the recognizer does not even depend on `k, v` surviving to Module 6 — it can fire from
the AST at Module-5 entry and hand Module 6 a fully-specified node. **Placement verdict: feasible; the plan's
location must be corrected from "Module-4 semantic pass" to "Module-5-entry AST pass."**

---

## 3. Recognizer pattern spec (closed-form, fail-closed)

A method is an **admissible T-A** iff its body is *exactly* (up to the payload holes):

```
def f(obj, acc):                      # exactly 2 relevant params: the walked subject + one accumulator
    if isinstance(obj, dict):
        [PRE]?                        # optional pre-action: literal-key reads (obj.get("K")==LIT / obj["K"])
                                      #   whose only write is acc.add(...) / acc |= ... (footprint ⊆ frame)
        for k, v in obj.items():      # generic iteration over the subject dict
            if k == "LIT": continue   # zero+ literal-key SKIP-guards (continue only)
            f(v, acc)                 # SELF-recursion on the iterated VALUE (same function name)
    elif isinstance(obj, list):
        for item in obj:
            f(item, acc)              # SELF-recursion on each list item
```
(`obj.values()` in place of `obj.items()` with no `k` is admissible; the `elif list` arm is required.)

**Admissible T-B** iff: structural self-recursion over `dict`/`List[dict]`, sub-terms read by **literal**
keys only, result is a **string** built by `+`/`"".join(...)`/f-string of recursive results, recursion on a
syntactic sub-term (list element or a fixed child key).

**Rejected — fail-closed (any one ⇒ no fire ⇒ method stays `\trusted`):**
1. `break` or `return` **inside** the walk loop. → *rejects `nearmiss_break`.*
2. Mutation of the **subject** during iteration: `del obj[k]`, `obj[k]=…`, `obj.pop`, `.append/.add` on the
   subject, or iterating a *snapshot* (`list(obj.items())`) as a hint of intended mutation. → *rejects
   `nearmiss_mutate`.*
3. Recursion to **any name other than `f` itself** (or to `f` on something that is not the iterated
   value/item). → *rejects `nearmiss_nonself`.*
4. **Non-literal** subscript/`.get` key (a variable/expression key), or `.items()` used with the key bound
   to anything but literal-equality skip-guards.
5. Pre-action or in-loop action whose write footprint is **not** within the declared frame (`acc` only).
6. Any statement kind outside {`isinstance` arms, literal-key skip-guard `continue`, the self-recursive
   call, the framed pre-action}. High emitter-helper fan-out (dispatcher) ⇒ reject.
7. The subject param not statically `Dict[str,Any]` / `Any`-narrowed-to-`dict` via the `isinstance` arms.

**Precision over recall:** a miss costs nothing (the method stays `\trusted`, exactly as today); a false
fire would break the additivity guarantee, so the spec rejects on *any* ambiguity. Byte-diff-0 across the
756-program corpus (0 programs match — phase2c datum) plus the poisoned control enforce inertness.

**Fixture cross-check (by inspection of the DONE negative controls):**
- `nearmiss_break.py` → rejected by rule 1 (`break` in the walk loop). ✓ must NOT fire.
- `nearmiss_mutate.py` → rejected by rule 2 (`del obj[k]` + `list(obj.items())`). ✓ must NOT fire.
- `nearmiss_nonself.py` → rejected by rule 3 (recurses to `_emit`, not self). ✓ must NOT fire.
- `poison_ta.py` → satisfies the admissible T-A pattern exactly (dict/list arms, `for k,v in obj.items()`
  literal skip-guard `continue`, self-recursion on `v`, by-ref `Set[str]` accumulator). ✓ MUST fire — the
  single corpus-external match that flips the byte-diff gate red once.

---

## 4. Negative-control fixtures (DONE — reused, not redone)

`test-suite/corpus/conformance/spikes/wall_v3_phase0/`:
- `nearmiss_break.py` — T-A shape + early `break` (rule-1 reject).
- `nearmiss_mutate.py` — T-A shape + subject mutation during iteration (rule-2 reject).
- `nearmiss_nonself.py` — walk shape + non-self recursion (rule-3 reject).
- `poison_ta.py` — exact T-A match; the poisoned control that must flip the byte-diff gate red once.

All four verified coherent against the §3 spec (above). They are committed with this doc.

---

## 5. Verdict and the honest alternative

**GO/NO-GO: NO-GO on the plan as written.** The closed pattern-class {T-A, T-B, accessor-only} covers
**24.2%** of the 541-method residual; **out-of-pattern is 75.8%** — a clear majority, dominated by
collection-result builders (259), non-self generic walks (33), and recursive predicates (16). The plan's
central claim (§0: "the residual is a *derived traversal* / closed catamorphism class") is **refuted by the
census** as a *majority* claim. Placement is *not* the blocker (feasible after relocating the recognizer to
Module-5 entry); **coverage is.**

**What is nonetheless true and worth banking (the refinement):** the **T-A generic-walk family is 22
methods** (10× the phase2c estimate of 2), concentrated in `core_ir_semantic.py`'s migrated Module-4 checks
and the IR-resolution passes. So a **scoped** build — the T-A template *only*, targeting the ~22-method
generic-walk family (with a second by-return sub-form for the functional folds), and ledgering everything
else `TRUSTED(essential)` — is a **defensible, bounded** proposition. That is a *different, smaller* plan than
v2-phase2c's "closed-class covers the residual," and its go/no-go should be re-costed on the ~22-method prize
(minus the payload-helper and functional-fold caveats in §1), **not** on a majority-coverage premise. The
T-A/T-B **template mechanism itself is unchanged**; only the *coverage claim* fails.

**Frozen-benchmark status unchanged:** items 1 (`find_named_expr_targets`, T-A) and 2 (`find_return_type`,
T-B) remain valid single-method targets — a scoped T-A/T-B build would still clear them; the census only
refutes the *extrapolation* from those two to the residual as a whole.

---

### Reproducibility
Census script + per-method feature dump: `scratchpad/census_v3.py`, `scratchpad/census_final_v3.json`
(541 rows, per-method file/class/name/bucket/reason/features). Every T-A and T-B row was verified by hand
against its live `src/pycsl` body; the accessor/out boundary was spot-checked (`_callable_tag_to_whyml`,
`_emit_bitwise_or_power` → accessor; `find_ghost_vars`, `_build_param_list` → out). Emitter erasure and
pipeline order read directly from `src/pycsl/frontend/Module5_IREmitter.py:1477` and `src/pycsl/pycsl.py`.
