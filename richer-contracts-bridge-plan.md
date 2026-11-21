# richer-contracts-bridge-plan.md — Bridging `src/formal-semantics` and `src/self-annotate` with richer contracts

*Self-contained plan, 2026-07-09. Successor to `the-finishable-path.md` (the coherence architecture),
sibling of the wall plans (`ir-traversal-…`, `value-model-…-plan-2`, `09-2223-plan`). Discipline carried
forward unchanged: spike-gated commitments, measured acceptance only, ledger fixed at 3, byte-diff-0
mirror-side gates, yields counted once, VALUE-not-count.*

**The gap, stated once.** Today the two trees make claims of very different strength and are connected
only by *audited prose links*: `src/formal-semantics` proves strong things (WP soundness `Phase4_WP.v` /
`Phase5b_Soundness.v`, per-arm emitters `Phase6L_Emit*.v`, per-handler correspondences
`Phase6e_Handle*English.v` / `Phase6e_Corr_Simple.v`, certified value shapes) about *formal objects*;
`src/self-annotate` proves weak things (`requires True / ensures True / assigns F` — type-safety, frame,
termination) about the *running mirror*. The connection is human: 26 comment-citations from
`pycsl-wp-spec.mlw` into `Phase4_WP.v`, the `arm-coverage.md` 5b boundary, the extraction byte-diff. The
Dafny comparison made the gap precise: per-method, the mirror's contracts say far less than
functional-correctness contracts would — **by design**, because the scope cut is what made three walls
tractable.

**The bridge principle (what "richer" must mean here).** Richer contracts must NOT mean "make SMT carry
semantics through reflective Python" — that re-opens every wall this campaign closed. It means:
**(i)** mirror contracts get to *reference formally-certified predicates and functions* (exported from
`src/formal-semantics` into WhyML) instead of `True`; **(ii)** the strongest contracts state *equality
with the extracted formal emitter* (`\result = emit_F …`), so SMT proves only a **string-builder
equality**, while the *meaning* of that string stays proved once, in Rocq/Lean, by the existing
coherence lemmas; **(iii)** every enriched contract is **generated from the formal side, never
hand-written**, so the bridge cannot drift. The end-to-end composition is the payoff:

```
  SMT (mirror, per method):   handler_F(args) = emit_F(args)          — C3 contract
  Rocq/Lean (formal, once):   eval_whyml (emit_F s) st = wp_F s st    — coherence lemma
  ⟹  the running handler's output performs the WP transformation      — Dafny-strength claim,
      (per method, mechanically, with SMT never touching semantics)      split across the bridge
```

The honest metric is not the ledger (it stays at 3) but the **footprint of `trusted_contracts_axiom`**:
every method lifted from `ensures True` to a checked richer contract shrinks what that axiom assumes.
The bridge's deliverable is a *contract-strength census* to sit beside the trusted-stub census.

---

## 0. The contract ladder (the plan's spine)

| Rung | Contract shape | What SMT must prove | Who is eligible |
|---|---|---|---|
| **C0** (today) | `requires True / ensures True / assigns F` | typing + variant + frame | everyone (floor, never removed) |
| **C1 — shape** | `ensures wf_pyval \result`, `ensures is_decoded \result`, record-field typing, `ensures length \result >= 0` | certified predicates applied to results; induction already done in Rocq/Lean | decoder outputs (M2), record builders, fold/template outputs |
| **C2 — structural/relational** | template-emitted relations: fold output domain ⊆ input keys, map-update footprint, decoder totality (`None ⇒ skipped`), fragment-grammar membership `in_emitted_fragment \result` | small lemma-pack facts; per-instance re-proof | **generator-emitted code only** (GenericFold/T1–T3, decoders) — the generator knows what it built, so it emits the ensures alongside the body |
| **C3 — semantic** | `ensures \result = emit_F_<arm>(args…)` where `emit_F_<arm>` is the **extracted** formal emitter | string-builder equality (concat normalization; no semantics) | straight-line handlers whose relevant state is capturable as arguments |
| **out of reach (named)** | `ensures eval(\result) = wp_F …` inside the mirror | semantics in SMT | nobody — this is what the coherence lemmas exist to avoid; Gödel/Löb bounds the self-referential version regardless |

Reflective/composition-wall methods are **capped at C1** (C2 where template-generated). Pushing them
higher re-opens `09-2223`; the cap is a rule, not a backlog.

---

## 1. P0 — The bridge infrastructure (the actual "bridge")

Three artifacts, all mechanical, all CI-checked:

1. **Predicate/function export.** A generated WhyML theory `pycsl-formal-export.mlw` containing:
   the certified predicates (`wf_pyval`, decoded-ness, record well-formedness — from
   `Phase2c_PyValDict.v` / `Phase2b_RecordVal`), and the **extracted per-arm emitters**
   `emit_F_assign`, `emit_F_if`, … from `Phase6L_EmitExtract.v` / `Phase6L_EmitSimple.v` (the extraction
   pipeline and its byte-diff harness already exist: `test-suite/extraction-byte-diff`). Hosting uses
   the M1 namespacing discipline from `09-2223-plan.md` (qualified `use … as F`), since this module must
   coexist with the emitter's own theories.
2. **The spec generator.** Contracts above C0 are **emitted, not written**: a generator reads the formal
   side (arm signatures from `Phase4_WP.v` / the `Phase6e_*` correspondence files; predicate names from
   the export) and produces the `#@` clauses for eligible mirror methods. Hand-written enriched contracts
   are rejected by lint — a hand-written `ensures` referencing `emit_F_*` is the drift vector this rule
   exists to kill.
3. **CI round-trip.** On every formal-side change: re-extract → regenerate `pycsl-formal-export.mlw` →
   regenerate contracts → mirror re-proves → ledger check (`Print Assumptions` / `#print axioms` = 3) →
   corpus byte-diff-0 (all of this is mirror-side; the §5.1 corpus impossibility from `09-2223` is
   untouched). The 26 prose citations in `pycsl-wp-spec.mlw` remain as documentation, but the *checked*
   link is now the round-trip.

---

## 2. The three spikes (gates before any rung is rolled out)

- **S-ext (gates P0/P1).** Extract **one** arm (`emit_F_assign`) plus `wf_pyval` into the export theory;
  host it in a mirror module alongside the emitter's own theories; type-check + empty-VC run.
  Falsifies: the extraction/namespacing story. Days.
- **S-c1 (gates P1).** Put `ensures is_decoded_func_list \result` on the M2 decoder and
  `ensures wf_record \result` on one record builder; whole-body prove. Falsifies: whether certified
  predicates discharge as postconditions within the SMT budget (expected cheap — the induction is done in
  Rocq/Lean; SMT only applies the predicate to the constructor spine). Days.
- **S-c3 (gates P3 — the load-bearing spike).** Prove **one** straight-line handler at
  `ensures \result = emit_F_assign x e`. **Named risk:** the handler builds its string by successive
  appends (possibly via helpers); `emit_F_assign` is a functional concat tree; the equality needs
  concat associativity/unit normalization. Mitigations, in order: (a) a small certified lemma pack
  (`concat_assoc`, `concat_unit`) + Why3 `compute_in_goal` on literal spines; (b) the **fragment-list
  encoding** — the generated contract states `fragments \result = emit_frags_F …` over a list of string
  fragments, with one certified lemma `concat (fragments s) = s`, so SMT proves list equality (easy)
  instead of string-theory equality (brittle). If both stall, C3 is not SMT-viable and the plan's C3 rung
  is **replaced by the per-run certificate** (finishable-path D3): same end-to-end claim, dynamic instead
  of static — an honest, already-designed fallback, not a failure.

---

## 3. Phases (each rung rolled out only after its spike, only to its eligible class)

- **P1 — C1 mirror-wide.** Shape postconditions wherever a certified predicate matches an output type:
  decoders, record builders, fold outputs. Expected to be the cheapest large win: it converts the
  certificates' inductions into per-method claims at near-zero SMT cost, and it is the first shrinkage of
  `trusted_contracts_axiom`'s footprint (a `\trusted` stub whose *ensures is now checked shape-truth* is
  assumed for less).
- **P2 — C2 on generator-emitted code.** GenericFold/T1–T3 and the M2 decoder generator emit their own
  relational ensures alongside the body (the generator knows the algebra; per-instance re-proof keeps it
  out of the TCB, as always). Also lands `in_emitted_fragment` — the grammar-membership predicate scoped
  to the fragment the evaluator axioms cover, which ties each emitting method to
  `evaluator-axiom-audit.md`'s boundary *by contract* rather than by prose.
- **P3 — C3 on straight-line handlers.** Post S-c3: roll `\result = emit_F_<arm>` across the handlers in
  `arm-coverage.md` whose state footprint is capturable as arguments. **Scoping rule (honest):** a
  handler that reads `self._indent`-style state gets `emit_F` extended with that argument (the spec
  generator computes the footprint from the frame); a handler whose output depends on state that cannot
  be captured as an argument, or that recurses into `_expr_to_whyml`, is **capped at C2** — recursing the
  equality through the expression emitter is verified-compiler-scale work and is exactly what the
  coherence-lemma side already covers once, formally.
- **P4 — the census + the theorem note.** Ship the contract-strength census (methods at C0/C1/C2/C3,
  alongside the trusted-stub count) and a short formal note in `src/formal-semantics` stating the
  composition at the top of this document as a theorem-schema: *for every method at C3 whose arm has a
  coherence lemma, the running mirror's output performs the WP transformation, modulo the 3-axiom
  ledger.* That note is the bridge's certificate.

---

## 4. Honest limits and non-goals

- **The walls stay closed by staying weak.** Reflective/composed methods (the `09-2223` class) are capped
  at C1/C2. Richer contracts there would put value invariants back into SMT through reflection — the
  precise thing three plans just spent a campaign routing around.
- **Gödel/Löb unchanged.** C3 + coherence yields per-method semantic correctness *relative to the 3-axiom
  ledger*; it does not and cannot make the system certify its own soundness from nothing. The metric is
  `trusted_contracts_axiom` footprint shrinkage, not ledger elimination.
- **Dafny parity, precisely claimed.** After P3, a C3 method carries a claim comparable to a Dafny
  functional contract — but obtained with SMT proving only string-builder equalities, semantics living in
  Rocq/Lean. That division of labor is the bridge; claiming more (e.g., functional contracts on the
  reflective class) would be claiming Dafny parity on code Dafny refuses to accept in the first place.
- **Drift is the failure mode to fear**, not unsoundness: an enriched contract that silently diverges
  from the formal side would be *checked* but *meaningless*. Hence P0's generate-don't-write rule and the
  CI round-trip — the bridge is only as good as its regeneration discipline.

---

## 5. Order and first action

`S-ext → P0 → S-c1 → P1 → P2 → S-c3 → (P3 | per-run-certificate fallback) → P4`.

First action: **S-ext** — extract `emit_F_assign` + `wf_pyval` into `pycsl-formal-export.mlw`, host it in
one mirror module under M1 namespacing, and run the empty-VC type-check. Hours-to-days, and everything
else on the bridge is blocked behind it.
