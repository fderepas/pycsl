# phase-b-expr-plan.md — Migrate the expression subsystem to typed `ExprIR`

> **Purpose.** Migrate Module 6's expression consumers (`_expr_to_whyml` and its
> ~30 helpers) from `Dict[str, Any]` to the typed `ExprIR` sums — the exact
> analogue of Phase B for statements. This is the **true Wave-1 prerequisite**
> identified by `semantic-ceiling-plan.md §12.3`: it is what makes the
> compositional `_handle_*` emitter methods even *capable* of a body-faithful
> contract (WI-C1/C4 there). It is a **representation change, byte-diff gated,
> and NOT ceiling-blocked** — unlike the body-faithful work it unblocks.
>
> **Grounding (measured).** The `ExprIR` types **already exist** — Phase A defined
> **85 `ExprIR` constructor classes** in `src/pycsl/ir_schema.py`, with
> `expr_from_dict` / `to_dict` converters and a passing round-trip test. This
> plan migrates the *consumers*, not the types. Scale: `expressions.py` is 3443
> lines, ~30 `Dict[str, Any]` consumer methods, **119** `expr["type"]` dispatch
> branches, and `_expr_to_whyml` has **169 call sites** across `module6_whyml/`.
>
> **Convention.** Named repo-root plan file; reference-corpus additions (WI-7);
> byte-identical gate after every batch (`bin/byte-diff-sweep.sh`, parallel).

---

## 0. Why this, and why now

`semantic-ceiling-plan.md §12` established that the compositional emitter handlers
(assign/if/while/for/return/try/…) cannot be made body-faithful because they all
call `_expr_to_whyml`, which is still `Dict[str, Any]` — a reflective
`expr["type"]` dispatch. Phase B migrated the **statement** side to typed
`StmtIR`; the **expression** side was never migrated. So:

- `_handle_*` bodies still call `stmt.value.to_dict()` (**41 sites**) precisely to
  feed the dict-typed `_expr_to_whyml` — the `.to_dict()` round-trip WI-C1 must
  eliminate cannot go until `_expr_to_whyml` accepts `ExprIR`.
- `_expr_to_whyml` cannot be given a *value contract* (WI-C4) while its input is
  `Any`-typed and its body is a reflective switch.

**Phase-B-expr removes that block.** It does not, by itself, verify anything — it
converts the representation so the *subsequent* verification work becomes
statable. It is the same kind of change that succeeded for statements (Phase B:
624-file byte-diff clean), so it is tractable and low-conceptual-risk, just large.

---

## 1. Objective & success criterion

**Objective.** `_expr_to_whyml` and its expression-consumer helpers take **typed
`ExprIR`** and dispatch by `isinstance` on the 85 `ExprIR` constructors; all 169
call sites pass `ExprIR`; the `expr["type"]` string switch is gone; the emitted
WhyML is **byte-identical** across the corpus at every step.

**Done =** no `Dict[str, Any]` expression signature remains in `expressions.py`
(and the expression-consuming parts of `statements.py`/`stmt_control_flow.py`);
`_expr_to_whyml(expr: ExprIR, …)`; the 41 `.to_dict()` sites in the statement
handlers that existed only to feed `_expr_to_whyml` are removed; **byte-diff 0**
across the full sweep; round-trip test still green.

---

## 2. Strategy — dual-representation, convert-at-boundary (mirror Phase B)

Phase B's safe pattern: convert the wire dict to a sum **once at the entry**
(`stmt_from_dict`), then dispatch by `isinstance`, keeping the emitted string
identical. Apply the same, with a **compatibility shim** so migration is
incremental and never breaks the build:

1. **Shim entry.** At the top of `_expr_to_whyml`, accept *either* representation
   during migration:
   ```python
   if isinstance(expr, dict):
       expr = expr_from_dict(expr)          # tolerate un-migrated callers
   ```
   Now the body can dispatch on the typed node while all 169 dict call sites keep
   working — **byte-identical from step 1.**
2. **Internal typed dispatch.** Replace the `expr["type"] == "…"` chain with
   `isinstance(expr, NumberExpr | VarExpr | BinOpExpr | …)` + typed field access
   (`expr.value`, `expr.left`, …). One expression-kind at a time; byte-diff after
   each batch.
3. **Migrate helpers.** Convert the ~30 `Dict[str, Any]` helper signatures
   (`_handle_binop`, `_handle_call_expr`, `_handle_subscript`, `_is_string_expr`,
   `_emit_membership`, …) to `ExprIR`, passing typed sub-nodes (`expr.left`, not
   `expr["left"]`).
4. **Migrate call sites.** Turn the 169 dict call sites into typed calls — most
   are already handed a typed sub-node (e.g. `stmt.value` is `ExprIR` post-Phase-B)
   and were only `.to_dict()`-ing to satisfy the old signature; delete the
   `.to_dict()`.
5. **Drop the shim.** Once all callers pass `ExprIR`, remove the step-1
   dict-tolerance shim. `expr_from_dict` is then called only at the true IR
   boundary (the wire → sum conversion), exactly like `stmt_from_dict`.

Every step is gated **byte-identical** — the sum is a pure in-memory
representation; the output WhyML never changes.

---

## 3. Work items

| WI | Item | Gate |
|---|---|---|
| **E1** | Shim entry on `_expr_to_whyml` (accept dict-or-`ExprIR` via `expr_from_dict`) | byte-diff 0 (no behavioural change) |
| **E2** | Convert `_expr_to_whyml`'s **leaf** kinds (Number/String/Var/Result/None/Raw) to `isinstance` + typed fields | byte-diff 0 |
| **E3** | Convert the **operator** kinds (BinOp/UnaryOp/Compare/BoolOp/bitwise/power) incl. `_handle_binop`, `_emit_bitwise_or_power` | byte-diff 0 |
| **E4** | Convert the **call** family (`_handle_call_expr`, `_handle_len_call`, `_handle_join_call`, `_handle_sum_call`, `_call_named_builtins`, `_content_string_method`, dict/getattr/isinstance lowerings) | byte-diff 0 |
| **E5** | Convert **subscript / slice / membership / comprehension** (`_handle_subscript`, `_emit_membership`, `_static_width`, `_linear_form`, iter/len) | byte-diff 0 |
| **E6** | Convert **container & typed-record** kinds (ArrayLit/Tuple/SetLit, TypedDict/NamedTuple access & literals, FieldGet) | byte-diff 0 |
| **E7** | Convert the **contract/ghost** expression paths (`_expr_to_whyml_string_ctx`, `_emit_contract_logic_symbol`, `_dotted_ensures_suffix`, membership in specs, `invariant_ctx`) | byte-diff 0 |
| **E8** | Migrate the **169 call sites** to pass `ExprIR`; delete the 41 statement-handler `.to_dict()` sites that only fed `_expr_to_whyml` | byte-diff 0 |
| **E9** | Drop the E1 shim; `_expr_to_whyml(expr: ExprIR, …)` final signature; remove all `Dict[str, Any]` expression signatures | byte-diff 0; round-trip green |
| **E10** | Reference corpus + LINK-1 note: ExprIR aligns constructor-wise with the formal `expr`/`contract_expr` inductive (as StmtIR did with Stmt); record in `ir-schema-spec.md` | corpus green; doc updated |

---

## 4. Sequencing (leaf-first over expression kinds)

```
E1 (shim, instant safety net; byte-diff 0)
 └─ E2 leaves  → E3 operators → E4 calls → E5 subscript/slice
       → E6 containers/records → E7 contract/ghost paths          [internal dispatch typed]
 └─ E8 call-site migration (delete .to_dict())  ← the payoff for semantic-ceiling C1
 └─ E9 drop shim + final typing
 └─ E10 corpus + LINK-1 doc
```

**Rationale.** E1 makes the whole subsystem migration-safe immediately (dict
callers tolerated). E2–E7 convert the *internals* kind-by-kind — each a small,
byte-diff-gated batch. E8 is where the ceiling-plan payoff lands: statement
handlers stop round-tripping through dicts. E9 finalizes the types.

---

## 5. What this unlocks — and what it does NOT (honest)

**Unlocks (the point):**
- `semantic-ceiling-plan.md` **WI-C1** — the 41 `.to_dict()` sites can be deleted;
  handler bodies read typed `ExprIR` fields.
- **WI-C4** — `_expr_to_whyml` becomes a typed-field function whose **value
  contract is statable** (it was `Any → str` before). This is the gate the
  compositional body-faithful work waited on.
- **LINK 1 for expressions** — `ExprIR` aligns constructor-by-constructor with the
  formal-semantics `expr`/`contract_expr` inductive (completing what Phase B did
  for `Stmt`/`StmtIR`).

**Does NOT do (do not overclaim):**
- It **verifies nothing.** It is a representation change; the emitted WhyML is
  byte-identical. No `_handle_*` is un-`\trusted` by this plan.
- It does **not** clear **Ceiling B** (semantic adequacy) — the string→state
  equivalence still rests on the audited evaluator axioms (`semantic-ceiling.md`).
- After it, the ceiling plan still needs **A2** (faithful models for
  `endswith`/`rsplit`/`replace`/`stable_hash`) and **A3** (a transpiler-state
  record for `assigns`) before a handler body actually proves.
- It is **not itself ceiling-blocked** — that is exactly why it is the right next
  lever: a tractable, gated migration, not a research problem.

---

## 6. Gate criteria

1. **Byte-identical** across the full sweep after **every** batch
   (`bin/byte-diff-sweep.sh`, parallel, `--no-typecheck`; `feedback_parallel_sweep`).
   A single byte difference fails the batch.
2. **Round-trip test** (`tests/test_ir_schema_roundtrip.py`) stays green.
3. **No `Dict[str, Any]` expression signature** remains at E9
   (grep gate on `expressions.py` + the expression paths of `statements.py`).
4. **Reference corpus** unaffected; add ≥1 `pycsl-reference` case per newly
   typed expression family if not already covered (`feedback_reference_corpus`).
5. **No new trust, no proof churn** — this touches only the transpiler; the
   Rocq/Lean proofs and the byte-diff harness are untouched.

---

## 7. Risks & mitigations

| Risk | Mitigation |
|---|---|
| **169 call sites** (vs. statements' 1 entry) — large surface | The E1 shim tolerates dict callers, so E8 migrates them *incrementally* with the build always green; no big-bang cut-over |
| Reflective helpers pass dicts among themselves | Migrate helper signatures in the same batch as their caller kind (E3–E7 grouped by family) |
| Contract/ghost expr paths (`invariant_ctx`, `_expr_to_whyml_string_ctx`) have subtle string-context behaviour | Isolate as E7, its own batch, with dedicated spec-context corpus cases |
| `expr_from_dict` fidelity gaps (an `OpaqueExpr` fallback for un-modeled shapes) | The round-trip test already walks 1127 nodes; extend it if E-batches surface an unmodeled shape (add the constructor, keep `OpaqueExpr` as the audited fallback) |
| Hidden `.get("type")` in non-`expressions.py` files | grep gate across `module6_whyml/` for `["type"]` / `.get("type")` on expression nodes at E9 |

---

## 8. Effort

| Phase | Effort | Risk | Note |
|---|---|---|---|
| E1 shim | Low | Very low | instant safety net |
| E2–E7 internals | High | Low (byte-gated) | ~30 helpers, 119 branches, kind-by-kind |
| E8 call sites | High | Low–Medium | 169 sites; mostly delete `.to_dict()` |
| E9 finalize | Low | Low | drop shim, type the signature |
| E10 corpus/doc | Low | Low | LINK-1 note |

**Overall:** a **Phase-B-scale** migration — mechanical but large (bigger than
Phase B: 169 call sites vs. 1 entry, 85 constructors vs. 24). Low conceptual risk
because it mirrors a completed, successful migration and is byte-diff gated
throughout. This is the honest cost the `semantic-ceiling-plan` under-counted.

---

## 9. Smallest first experiment (validate the pattern on one kind)

**E1 + E2-for-`Number` only:**
1. Add the dict-tolerance shim to `_expr_to_whyml` (E1).
2. Replace the `if t == "Number":` branch with `if isinstance(expr, NumberExpr):`
   reading `expr.value` (typed) instead of `expr["value"]`.
3. Byte-diff sweep: **must be 0**.

If step 3 is clean, the dual-representation pattern is validated and E2–E9 are its
systematic repetition. If a byte difference appears, it localizes a fidelity gap
in `expr_from_dict`/`NumberExpr` (e.g. the float/`real` lowering) to fix before
scaling — cheap, early, and exactly the kind of issue Phase B also ironed out
per-kind. This mirrors the Phase-B execution discipline that reached 624-file
byte-clean.
