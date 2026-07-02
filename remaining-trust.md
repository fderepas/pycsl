# remaining-trust.md — the two remaining trust surfaces (items 3 & 4), assessed honestly

The 12 reflecting-family statement handlers now verify their own bodies (type-safety + a
checked `assigns` frame). This doc records the two remaining trust surfaces and their honest
status — one **irreducible** (item 3), one a **scoped fresh campaign** (item 4).

---

## Item 3 — value contracts for the recursion leaves (`_expr_to_whyml` / `_stmts_to_whyml`)

**Status: IRREDUCIBLE (Ceiling B, Gödel/Löb). Not soundly achievable — by design.**

The 12 handlers prove `requires True / ensures True / assigns <frame>` — **type-safety +
frame**, not value-faithful `ensures \result == <the exact WhyML string>`. Value-faithfulness
would require the recursion leaves `_expr_to_whyml` / `_stmts_to_whyml` (still `\trusted`
stubs) to carry **value contracts** stating exactly what they emit. But those siblings *are*
the emitter's own recursive expression/statement logic — giving them a value-faithful contract
means proving the emitter emits a WhyML string that, WHEN EVALUATED, performs the WP
transformation. That is the **metacircular core**: a system cannot prove the soundness of its
own evaluator (Gödel's 2nd incompleteness / Löb). `semantic-ceiling-plan.md §0`,
`facing-the-facts.md §3.1/§5`, and `src/self-annotate/semantic-ceiling.md` establish this;
`a2-a3-plan.md §7` and `semantic-ceiling-plan.md §7` name it a **non-goal**.

**What "doing it" would (dishonestly) require** is a fake axiom (an `Axiom`/`Admitted`/
tautology asserting the evaluator sound) — explicitly forbidden by the doctrine
(`pycsl-how-to-develop §8.4`, "Cited axioms must be REAL").

**The sound handling already in place (stratification, not elimination).** The maximal *sound*
result is the coherence route: `src/self-annotate/pycsl-wp-spec.mlw` proves, per WP arm,
`eval_whyml_stmts (handle_X_code …) st = wp_X … st` from a single **audited evaluator axiom**
`X_semantics` (the enumerated D2 boundary, `evaluator-axiom-audit.md`), and LINK-2
(`bin/extraction-byte-diff.sh`) byte-diffs the Rocq-extracted emitter against this one. So the
emitter's correctness reduces to: a proved coherence lemma + **one audited axiom per
construct** — the maximal "break" Gödel/Löb permits. The `\trusted` recursion-leaf stubs are
re-sited onto that audited boundary (`arm-coverage.md`), not a silent hole.

**Verdict:** item 3 is complete in the only sound sense (stratified to the audited D2 axioms).
Un-`\trusting` the siblings with value-faithful contracts is provably unavailable.

---

## Item 4 — un-`\trust` the control-flow statement family (`if`/`while`/`for`/`return`/`try`/`match`)

**Status: a SCOPED FRESH CAMPAIGN (engineering-possible, not ceiling-blocked) — a defined
follow-on, comparable in scope to the just-completed reflecting-family arc.**

The control-flow handlers live in the `ControlFlowStmtMixin` mirror
(`src/self-annotate/src/module6_whyml/stmt_control_flow.py`) as **fake-body stubs** —
`def _handle_while_stmt(self, stmt: int, …) -> str: return ""`. Un-`\trusting` them is NOT the
Ceiling-B problem (item 3); it is porting each handler's REAL body into the mirror and proving
it, exactly as was done for the 12 reflecting-family handlers. It is bounded, but real:

**Structural prerequisites (before any handler):**
1. Make `ControlFlowStmtMixin` a `@mutable_state @dataclass` (today it is a plain mixin) so the
   `emit_ir` / string-local / seq machinery fires for its bodies.
2. Declare the state it reads: `_has_early_ret: int`, `_func_return_type: str`,
   `_current_tuple_arity: int`, plus the already-declared `_seq_locals`/`_array_locals`.
3. Cross-file sibling stubs (`-> str`): `_materialize_bridge`, `_materialize_str_bridge`,
   `_maybe_inject_union_return`, `_seq_init_expr`, `_bool_ir_to_int_wrap`, `_stmts_to_whyml`,
   `_expr_to_whyml` (the last two already exist in the statements mirror).
4. Wire `stmt_control_flow.py` into `bin/run-self-annotation-suite.sh` (it is not currently
   a separately-verified suite entry).

**Per-handler difficulty (measured):**
- `_handle_return_stmt` — 126 lines, **read-only** (`assigns \nothing`), reflects on `val_ir`,
  handles seq/array/string/tuple/union returns via materialize bridges + `_seq_init_expr`. The
  *most self-contained* → the natural first target.
- `_handle_if_stmt` / `_handle_while_stmt` / `_handle_for_stmt` — compositional: reflect on the
  IR, recurse via `_stmts_to_whyml`, and (while/for) emit loop invariants/variants. The for-loop
  needs the same `0 <= idx` / variant discipline SQ5 added.
- `_handle_try_stmt` / `_handle_match_stmt` — the broadest (handler tables, exception arms).

**Why it is a campaign, not a quick item:** each handler is a multi-iteration port+prove of the
same magnitude as one of the 12 already landed (each of those took ~10 gated iterations). The
infrastructure now EXISTS (emit_ir ADT, string-locals, seq model, self.ir slice, form-complete
reflection router), so the per-handler cost is lower than the first ones — but the structural
setup + ~6 compositional handlers is genuinely a fresh arc.

**Verdict:** item 4 is a well-scoped, ceiling-free follow-on. Recommended sequence: structural
setup → `_handle_return_stmt` (read-only leaf) → `if`/`while`/`for` (with the SQ5 loop
discipline) → `try`/`match`. Its own plan (`control-flow-family.md`) when taken up.

---

## Summary

| item | status |
|---|---|
| 3 — recursion-leaf value contracts | **irreducible (Ceiling B)** — sound handling is the stratified D2 axioms; full value-faithfulness is Gödel/Löb-unavailable |
| 4 — control-flow handler family | **scoped fresh campaign** — engineering-possible; structural setup + ~6 compositional ports; not ceiling-blocked |
