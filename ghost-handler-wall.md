# The Ghost-Handler wall — a reviewer's map of `ensures True` projection faithfulness

*External-review statement, 2026-07-13, produced by the self-tcb-reduction-driver (escalated as a
breakability-unknown wall). Self-contained: assumes no prior PyCSL knowledge. It asks the reviewer to
RUN Why3 and adjudicate a load-bearing question the sub-loop could not settle by reasoning: **under a fixed
type-safety-only contract, is a "distinct-but-value-unfaithful" projection a sound, legitimate conversion —
or a facade? And is there a faithful mechanism for the swap case?** Every claim is reproducible from cited
evidence.*

---

## 1. Global picture (what PyCSL is, and where this sits)

**PyCSL** is a deductive verifier for a Python subset: it compiles annotated Python through a 6-module
pipeline into **WhyML** (the [Why3](http://why3.org) language), discharged by SMT (Alt-Ergo, Z3) and, when
those fail, Rocq/Lean. It **verifies a mirror of its own emitter**: the compiler's WhyML-generation code is
itself annotated Python that PyCSL proves. The self-verification campaign converts the mirror's `\trusted`
stubs (assumed contracts) into verified bodies, each held to three disjoint oracles (fidelity to the live
code, Why3 discharge, corpus byte-diff-0). A **standing scope cut** governs every conversion: the fixed
contract shape is `#@ requires True / ensures True / assigns <frame>` — **type-safety + termination + frame
only, NEVER value-faithful**. The 3-axiom Rocq/Lean ledger must stay at 3.

## 2. The method class and the machinery

`expr_ghost_collections.py` / `expr_ghost_spec_ops.py` hold ~34 **ghost expression handlers**:
`(self, node: ExprIR, …) -> str`. Each reads named `ExprIR` children of `node` and builds a fixed WhyML
string. The mirror models `node` as an `emit_ir` value — a WhyML variant (`IrVar | IrStr | IrBinOp op left
right | IrSub v idx | IrOther | …`) with **projectors** and proven `size`-decrease lemmas:
- `left_of e = match e with IrBinOp _ l _ -> l | _ -> IrOther ""` (with lemma `is_binop e -> size(left_of e) < size e`)
- `right_of e = match e with IrBinOp _ _ r -> r | _ -> IrOther ""`
- `svalue_of e = match e with IrSub v _ -> v | _ -> IrOther ""`

The emitter lowers a Python attribute read `node.<attr>` to one of these projectors via a name→projector
table `_EMIT_IR_NODE_ATTRS = {"dict":"left_of","key":"right_of","left":"left_of","right":"right_of","lo":"left_of","hi":"right_of",…}`.
An unmapped attr falls through to `svalue_of`. ~21 handlers are converted this way (`map_get`, `cons`,
`map_set`, etc.); each `--fun`-proves under `ensures True`.

## 3. The wall — three open questions the sub-loop could not settle

### Q1 (LOAD-BEARING): is a value-unfaithful projection sound + legitimate, or a facade?

The remaining handlers include a **position-swap** family: `SetAddExpr(set, elem)` vs `SetMemExpr(elem,
set)` — the attribute **name** `elem` is field-1 in one subclass, field-2 in the other. A single global
name→projector map cannot map `elem`/`set` to the *correct* child in both. Concretely, to convert
`_handle_set_mem_expr` (`s = self._e(node.set); e = self._e(node.elem)`) one could map `set → left_of` — but
for `SetMemExpr(elem, set)`, `left_of` returns the FIRST child (`elem`), so `node.set` projects to `elem`'s
value. The two projections (`left_of node`, `svalue_of node`) are **syntactically distinct** and both
**size-bounded** (so termination discharges) — but the projection is **value-WRONG** (it recurses on the
wrong child). Under `ensures True`, the goal has no value obligation, so `--fun` reports SUCCESS.

Already-committed conversions sit on a spectrum of this: `map_get` (`dict→left_of, key→right_of`) is
value-FAITHFUL *if* a MapGet node is modeled as an `IrBinOp` with `dict=left, key=right`; but `map_set`'s
third child `value → svalue_of` returns the `IrOther ""` **sentinel** for a non-`IrSub` node — a
value-UNfaithful projection already accepted (commit `5221ef3d`).

**The question for the oracle:** under this campaign's fixed `type-safety+termination+frame`, never-value-faithful
contract, is a conversion whose emitted body recurses on a *size-bounded but semantically-wrong* sub-node
(or the `IrOther ""` sentinel) a **SOUND, legitimate** marker reduction (it genuinely proves the handler
type-safe + terminating — real content), or does it cross into **VACUITY/facade** (the campaign's
non-vacuity rule: "reads real accessors, no opaque projection")? `left_of`/`svalue_of` ARE real, lemma-backed
projectors — but do they "read a real accessor" in the campaign's sense when they demonstrably return the
wrong child / a constant sentinel? Is there a principled line (e.g. "distinct + size-bounded + real projector
= sound" vs "must be the faithful child")? **RUN a spike**: model a 2-child node both ways (faithful vs
swapped/sentinel projection), prove both under `ensures True`, and judge whether the swapped one is a
genuine type-safety proof or a degenerate one — and whether accepting it threatens soundness of the
self-verification (does proving a *model* that recurses on the wrong child still soundly establish the *real*
handler's type-safety + termination?).

### Q2: is there a FAITHFUL mechanism for the swap case?

The emitter's attribute-lowering site (`_handle_attribute_expr`) sees only the attr NAME, not the node's
`ExprIR` **subtype** (all live handlers type `node: "ExprIR"` base). Is a faithful position-based projection
recoverable — e.g. by threading the handler's subtype (each handler statically handles one subclass), a
per-subtype field-index table from the schema, or a different emit_ir modeling of these nodes — WITHOUT a
new axiom and WITHOUT changing the live source? Or is faithful disambiguation a genuine boundary here?

### Q3: two singletons — bounded or boundary?

- `_handle_ctor_test_expr`: emits `Array.make !arity "_"`; the abstract arity getter has no `ensures result
  >= 0`, so Why3's `Array.make` precond `n >= 0` is undischargeable. Is a bounded fix available (a
  nonneg-safe abstract getter contract) axiom-free, or a boundary?
- `_handle_mktuple_expr`: variadic `node.elts` (a list of sub-nodes). Is a `list`-child projection + fold
  expressible/provable under `ensures True`, or a boundary?

## 4. Why this is a fair lens / honest limits

The reader-ADT foundation (projectors + `size` + decrease lemmas) is certified and reproduces
(`preamble.py::_emit_exprir_theory`). The 3-axiom ledger is untouched by any of this. The **only** genuinely
undecided point is Q1 — a *doctrine/soundness* question about how far the `ensures True` scope cut extends —
which the sub-loop kept re-reasoning without resolving, and which determines whether ~7 remaining handlers
(the swap family + relatives) are a free drain or must stay `\trusted`. A review that only re-reasons from
this prose adds nothing; the ask is a **Why3 spike** that settles Q1 (and probes Q2/Q3) with a run.

## 5. What this review must produce

Write `ghost-handler-wall-response.md` with a hand `.mlw` spike (proven with `why3 prove`, `^axiom ` = 0) and
a verdict: for **Q1**, is the value-unfaithful (swapped/sentinel) projection a SOUND, campaign-legitimate
type-safety conversion, or a facade to REJECT — with the soundness argument (does the model faithfully
establish the real handler's type-safety+termination despite recursing on the wrong child?) and, if legitimate,
the exact non-vacuity criterion that distinguishes it from an opaque stub. For **Q2/Q3**, BOUNDED-FEATURE vs
BOUNDARY, each with the spike evidence. That verdict — not the prose — is the deliverable.
