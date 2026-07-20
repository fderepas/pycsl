# pyval-value-model-wall-impl.md — implementation plan (spike PASSED; emission-refutation exit)

Synthesized from `pyval-value-model-wall.md` + `pyval-value-model-wall-response.md` (Gate R **CONFIRM**, one
refinement). The make-or-break MODELING spike is already PROVEN by the fable oracle
(`getting-better/pyval-oracle.mlw`, Z3 Valid, axiom-free). The impl make-or-break is now **EMISSION**: can the
tool emit that exact certified theory + a faithful dict build/read, gated + byte-inert?

## The CERTIFIED shape (emit EXACTLY this — from the proven oracle)
```
type pyval = PStr string | PInt int | PArr pyval_list | PMap (map string (option pyval)) | PNode pyval
with pyval_list = PNil | PCons pyval pyval_list
```
- **`PArr` MUST use bespoke `pyval_list` (PNil/PCons), NOT `seq pyval`** (Why3 rejects `seq` recursion as
  non-strictly-positive — the hard refinement). `PMap (map string (option pyval))` is ACCEPTED (positive codomain).
- **Structural mutual recursion, NO `variant` clause** (the `irlist`/`stmt_list` fold shape — Why3 emits no
  termination VC). `get = Map.get`. Reads are key-projection (no fold into map values needed for the frontier).
- **Node arm:** the oracle proved `PNode pyval`; if unifying with the certified `emit_ir` ADT reintroduces a
  positivity issue, KEEP `PNode pyval` (proven). Decide by typecheck.
- Axiom-free; the `size v >= 1` lemma needs a 3-line mutual-induction side-car (Coq+Lean) — but NO fold in the
  frontier requires `size`, so `size`+its lemma are cert-only (not emitted into VCs).

## Gate S — EMISSION make-or-break (re-confirm oracle, then first emit). Refutation exit.
1. Driver re-proves the oracle (`why3 prove -P z3 getting-better/pyval-oracle.mlw`) — must reproduce Valid + axiom-free.
2. Emit the `pyval` theory into `preamble.py` (gated on a NEW `_uses_pyval` signal) + a reference fixture that
   builds+reads a heterogeneous dict; `pycsl <fixture> --keep-mlw`; confirm the emitted theory TYPECHECKS.
   - PASS → build I1 fully.
   - REFUTE (the tool can't emit the strictly-positive bespoke variant, or the fixture won't typecheck/prove,
     or `_uses_pyval` can't gate byte-inertly) → CERTIFIED-BOUNDARY: the model is Why3-viable but EMISSION-walled.
     Record + stop; do NOT grind.

## Build increments (each driver-verified; COUPLING RULE §5: cert co-lands with the capability)
- **I1 — infra + cert + fixture (NO mirror conversion yet):**
  (a) `preamble.py::_emit_pyval_theory` gated on `_uses_pyval` — emits the certified variant (constructive).
  (b) dict-literal emitter: `{k: v}` where the values are heterogeneous → `map string (option pyval)` via
      `Map.set` chains, per-value tag (str-lit/str-var→`PStr`, int→`PInt`, list→`PArr` cons, nested-dict→`PMap`,
      IR-node→`PNode`). Gated on `_uses_pyval`.
  (c) typed readers: `d[k]` → `Map.get d k` projecting the arm.
  (d) **`src/formal-semantics/rocq/Phase2f_PyVal.v` + `lean/Phase2f_PyVal.lean`** — the variant + `size` +
      `size_pos` (3-line mutual induction), AXIOM-FREE (`Print Assumptions`/`#print axioms` = clean; ledger 3).
  (e) reference fixture `test-suite/corpus/pycsl-reference/09xx_pyval_heterogeneous_dict.mlw` (git add -f) that
      builds `{"pattern":lit,"ctor":var,"captures":[...]}` + reads each faithfully (non-vacuous; evil-twin).
  Gate: fixture PROVES; byte-diff-0 (gated on `_uses_pyval` ⇒ corpus-inert — the 767 baseline unchanged); ledger 3.
- **I2 — the make-or-break CONVERSION:** convert `_render_match_pattern` (mirror `stmt_control_flow.py`) — the
  simplest heterogeneous-dict build+read — to a verified body via the pyval model. Gate: whole-file proof
  SUCCESS (foreground), fidelity (mirror==live verbatim), count strictly down, MUTATION TEST (change a dict
  value tag → emitted .mlw changes), byte-diff-0.
- **I3+ cascade (follow-on):** the Dict-of-Dict collectors (`_collect_typevar_registry`/`_collect_type_params`/
  `_collect_class_fields`), then the giants (`_emit_ir_args_recv_ir` → `_is_emit_ir_expr`), then the 2
  faithfulness bugs (Bug 1 dict-literal already fixed; Bug 2 negative-slice). Each its own gated increment.

## Gate battery (per increment — driver-verifier FRESH)
Fidelity ∧ whole-file Why3 proof SUCCESS ∧ byte-diff-0 (gated on `_uses_pyval`; or M1 sanctioned-reset+reprove)
∧ ledger==3 (`Print Assumptions`/`#print axioms` on Phase2f) ∧ count strictly down ∧ non-vacuity (MUTATION TEST;
real pyval constructors, no int-hash/int-erasure). The cert co-lands in the SAME commit as the capability (§5).

## Honest costed scope
I1 (theory+emitter+readers+cert+fixture) is the foundation (the risky coupling unit). I2 is the first count cut.
I3+ is the cascade (the giants + collectors — the bulk of the yield). Multi-session; this run targets I1 + I2 +
as much of I3 as fits. Refutation exit at Gate S if EMISSION walls (the model is proven; the tool's emission is
the residual risk).
