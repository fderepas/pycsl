# pycsl-prereqs-spec.md — the P-series: core/PyCSL prerequisites for the C front-end (and beyond)

**Date:** 2026-06-10
**Status:** Specification (for review — no code changed)
**Owner:** [CORE] (`src/pycsl/ir_schema.py`, `core_ir_semantic.py`, `Module6` + `module6_whyml/`) +
[FRONTEND-PY] (`src/pycsl/frontend/` — Modules 2 & 5) — **not** [FRONTEND-C]; everything here lands
in the PyCSL repo under PyCSL's own gates, *before* the CCSL phase that consumes it.
**Origin:** `c-front.md` (rev. 6) §13 — promoted to a dedicated spec; `ir.md` (the wire contract +
versioning policy); `refactor.md` (the laws and the standing gate); `07-1705-spec-rev4` (the
seq/ref/view model P-2 generalizes).
**Consumed by:** CCSL phases P0/P1/P3/P5 — and, by design, every future front-end (Rust, Go): each
P-item is justified only because it is a **platform** change, never a C-only accommodation.

---

## 1. Purpose, scope, and the one rule

Four prerequisites (P-1…P-4) were identified when the C front-end's open design choices were
resolved (`c-front.md` §12): two starred as globally impactful (typed binders, the borrow model) and
two implied by choosing the core-feature option (`loop assigns` in Module 6; `\at` label anchors).
This spec details each: motivation, design, exact change surface, IR-version impact, gates, and
ordering.

**The one rule:** every P-item is an ordinary PyCSL change, governed by `refactor.md`'s laws —
behaviour-preserving and corpus-gated (byte-diff, determinism re-verified 4–5×), fail-loud, TCB
ledger unchanged or shrunk — and additionally by the Phase-E conformance corpora: the **core-only**
goldens (28/28) and **frontend-only** goldens must remain byte/structure-identical, since every
P-item is additive and opt-in. A P-item that changes an existing driver's emission has violated its
own contract.

**IR versioning (per `ir.md` §2):** P-1 and P-4 require **no schema change**. P-3 adds one optional
field → **IR 1.2** (additive minor; `ACCEPTED_IR_VERSIONS` widens to {1.0, 1.1, 1.2}; a 1.1 document
stays ingestable; round-trip identity re-verified). P-2's eventual nodes are a later additive bump
(1.3) — its v1 deliverable is a *design spec*, not schema.

## 2. P-1 — Typed quantifier binders, with ACSL's `integer` *(consumed by CCSL P1)*

**Motivation.** One binder convention across all front-ends; the core's typed-binder check
(`core_ir_semantic`: an unresolved `binder_type` is rejected) stops depending on per-front-end
inference quality; and the ACSL alignment imports the load-bearing **`integer` vs concrete-type
distinction** — quantify over the mathematical integers by default, over a bounded C type only when
you mean its range.

**Design.**
- **Grammar (Module 2):** the binder position accepts a type name: `\forall integer k. E`,
  `\forall int k. E` *(in PyCSL both map to math int — PyCSL's `int` IS `integer`; the distinction
  becomes real only in bounded-type front-ends like C, where `\forall int k;` desugars front-end-side
  to `integer` + the type's range as `domain`)*, `\forall MyClass c. E`, `\forall Option o. E`.
  `integer` is a new keyword normalizing to the IR tag `"int"`.
- **Emission (Module 5):** a typed binder fills `Forall/Exists.binder_type` **directly** — no
  inference pass involved. The existing IR field is used as-is; classes/datatypes resolve against
  `type_decls` exactly as the migrated `quant_binders` check expects.
- **Untyped binders** remain accepted via the existing inference (additive; the corpus is untouched).
  Their *fate* is fixed — deprecated, since ACSL has no untyped binder — with only the **horizon**
  open (`c-front.md` O-6: docs mark typed as the form; corpus migration scheduled separately).
- **IR impact: none.** `binder_type` already exists; this is grammar + emitter + docs.

**Gates.** Standing gate (§1) **plus**: drivers for each binder-type class (`integer`, concrete
class, datatype, and the *negative* — an unknown type name is a located error, exactly the existing
core check); corpus byte-identical (no existing driver uses the new syntax); doc-coherency picks up
the `integer` keyword.

**Acceptance.** `\forall integer k. 0 <= k ==> …` round-trips through dump → ingest → prove —
**[PROVE]**; an unknown binder type is rejected with the existing located message — **[PROVE-neg]**;
corpus + both conformance corpora untouched — **[byte-diff]**.

## 3. P-2 — The borrow-shaped mutable-reference model *(design now; implementation consumed by CCSL P5 and the Rust front-end)*

**Motivation.** Three front-ends need the *same* missing capability: C scalar out-params
(`int *out`), Rust `&mut`, Go pointers/slices-into-arrays. Designing it once, before two front-ends
exist, prevents two incompatible ad-hoc answers — this is the single highest-leverage IR design
decision on the roadmap, and the reason it is a **prerequisite in design even though it is not on
CCSL v1's critical path** (CCSL v1 rejects out-params with a hint naming this future).

**What this spec mandates (and deliberately does *not* decide).** P-2's v1 deliverable is **its own
design specification** (`c-front.md` O-5), answering at minimum:
- **The model shape.** The validated starting point is the seq/ref/view result
  (`07-1705-spec-rev4`, grounded by the 07-1732 probes: a `ref (array int)` cannot be rebound — #8 —
  but a `ref (seq int)` can — #9): *value = immutable view, mutation = region-free `ref` rebind*,
  the Creusot shape, **without prophecy** (Why3 reasons about a region-free ref's before/after
  directly; prophecy targets mutation-through-borrow obstacles we should prove we have before paying
  for). The design must state where that model suffices (scalar out-param `int*` ≈ `ref int` —
  Why3-native) and where it does not (struct borrows, reborrowing, two-phase aliasing).
- **Aliasing discipline.** `f(&x, &x)` — rejected, `\separated`-obligated, or statically excluded?
  Fail-loud is the floor; the design chooses the mechanism.
- **IR surface.** Additive node/field shapes (a borrow-param marker? a `RefCell` value node?), with
  the explicit constraint that a 1.2 document without them remains valid (additive 1.3).
- **Soundness obligations,** stated O-style: a write through a borrow is visible to the lender
  (no silent copy); an aliased mutable borrow can never be silently admitted.

**Stage gates.** D0: the design spec, reviewed. D1: a *feasibility probe in Why3* for each load-
bearing claim (the "prove the rebind first" discipline — the seq probes are the template). D2: the
minimal IR + Module 6 lowering, gated by its own drivers. D3: first consumer (CCSL out-params).

**Acceptance (for the P-2 design phase).** The design spec exists, names its probes, and each probe
has a recorded verdict before D2 begins — **[probe-gated]**; nothing in PyCSL changes until D2 —
**[byte-diff trivially]**.

## 4. P-3 — `loop assigns` as a core feature *(consumed by CCSL P3; requires P-4)*

**Motivation.** Chosen over the front-end desugar (`c-front.md` 12.1b) because Why3 loops have no
`writes` clause — whoever implements `loop assigns` must synthesize the preservation reasoning, and
doing it **once in Module 6** gives it to every front-end; the Python surface (`#@ loop assigns`)
ships in the same change — the platform payoff that justified (b).

**Design.**
- **IR (the 1.2 addition):** an optional `assigns` field on `While`/`For` statement nodes — a list of
  expr-IR targets, the same shapes `contracts.assigns` carries (`Var`, `FieldGet`, `AssignsRegion`
  for `a[lo..hi]`, `Nothing`). Absent ⇒ today's behaviour, byte-identical.
- **Module 6 encoding — the two halves, both fail-loud:**
  - **Scalar / field targets (the obligation half):** Module 6 already computes the loop body's write
    effects; it **checks the computed write set ⊆ the declared targets** and rejects (located error)
    a write outside the clause — the loop-frame analogue of the function-`assigns` frame VC, and the
    half that makes `loop assigns` a *claim that is checked*, never an assumption.
  - **Array / region targets (the payoff half):** Why3 havocs a written array wholesale across the
    loop; for each declared region `a[lo..hi]`, Module 6 synthesizes the complement-preservation
    invariant — `∀k. ¬(lo ≤ k ≤ hi) ⟹ a[k] = (a at LoopEntry)[k]` — using a `LoopEntry` label
    emitted immediately before the loop (**hence P-4**). This invariant is simultaneously the
    *payoff* (unhavocked knowledge of the untouched cells — the region-scoped preservation that
    HAPPY/coupling reasoning wants) and the *obligation* (a body writing outside the region fails the
    invariant's preservation proof). No separate frame check is needed for regions.
- **Surfaces:** PyCSL `#@ loop assigns a[lo..hi], self.f` (Module 2); CCSL `//@ loop assigns …`
  (already specced). Clause-presence is opt-in per loop.

**Gates.** Standing gate (§1); **byte-identical emission for every loop without the clause** (the
opt-in proof, the Track-B P1 pattern); drivers: a region-scoped loop whose post-loop proof *needs*
the complement preservation (proves with the clause, doesn't without — the payoff demonstrated); the
negative — a body writing a scalar outside the clause is **rejected**, a body writing outside the
declared region **fails the invariant** — **[PROVE-neg ×2]**; os + formal_0001 + both conformance
corpora green; IR 1.2 round-trip identity.

**Acceptance.** Opt-in byte-diff; payoff driver **[PROVE]**; both fail-loud negatives; `#@ loop
assigns` documented + doc-coherency green; `ir.md` updated for 1.2.

## 5. P-4 — Arbitrary `\at` label anchors in Module 6 *(probe at CCSL P0; required by P-3)*

**Motivation.** Two consumers: P-3's `LoopEntry` encoding, and the resolved CCSL decision (12.4)
that user C labels serve as `\at` anchors. The IR already carries both halves (`At {expr, label}`;
the `Label` statement) — what is unknown is Module 6's lowering breadth.

**Design.**
- **Probe first** (the verdict is CCSL P0's deliverable): does Module 6 today lower `Label` +
  `At{label}` for an arbitrary label, or only the built-ins riding on `old`?
- **If the gap is real (expected):** Module 6 maps `Label name` → WhyML `label Name in …` at the
  statement position, and `At{e, L}` → `e at Name`; `Pre`/`Old` keep their existing `old`-based
  lowering; `LoopEntry` is not user-written — Module 6 *emits* it before any loop carrying a P-3
  clause (and for user `\at(·, LoopEntry)` in that loop's invariants). Label names sanitize to valid
  WhyML marks deterministically (content-ordered, per the determinism law).
- **IR impact: none** — existing nodes, broader lowering.

**Gates.** Standing gate; drivers: a ghost label + `\at` read-back proves; an undeclared label in
`\at` is a located error **[PROVE-neg]**; corpus byte-identical (no existing driver emits the new
lowering).

## 6. The reliefs — decided items that need NO core change (the boundary of this spec)

For the record, because they bound the core footprint: the uninitialized-read **taint** (ghost
`GhostAssign` flags + `ProofAssert` checks — existing nodes), the per-function **unsigned pragma**
(emission-side; the manifest records the mode), **full annotation preprocessing** (front-end, with
its expansion map), **`compile_commands.json` + the cross-TU drift check** (front-end tooling), and
the **division guard** (status quo). The C front-end's core footprint is **P-1…P-4 and nothing
else** — `c-front.md` acceptance #1 holds the line, and this spec is its bill of materials.

## 7. Sequencing & dependency graph

```
P-1 (grammar/emitter; no IR change)  ──────────────▶ consumed by CCSL P1
P-4 probe ──▶ P-4 lowering (if gap) ──▶ P-3 (IR 1.2 + Module 6) ──▶ consumed by CCSL P3
P-2 D0 design spec ──▶ D1 probes ──▶ D2 IR+lowering (1.3) ──▶ D3 = CCSL P5 out-params / Rust
```

- **P-1 first** — cheapest, independent, unblocks the C dialect's binder grammar.
- **P-4 before P-3** — `LoopEntry` is P-3's encoding mechanism; the probe runs at CCSL P0 so its
  verdict is in hand before P-3 is scheduled.
- **P-2 design in parallel, implementation deliberately last** — broadest payoff, longest lead time,
  not on CCSL v1's critical path.
- Each item ships independently and reversibly (refactor.md law §1); no item starts before the
  previous gate is green *within its own chain* (the two chains are independent).

## 8. Acceptance criteria (spec-level)

1. **Additivity is total:** after each P-item, the reference corpus, the core-only goldens (28/28),
   and the frontend-only goldens are byte/structure-identical; determinism re-verified 4–5× —
   **[byte-diff / measure]**.
2. **P-1:** typed binders (incl. `integer`) prove end-to-end; unknown type rejected — **[PROVE /
   PROVE-neg]**.
3. **P-2:** the design spec + probe verdicts exist before any code; no schema change before D2 —
   **[probe-gated]**.
4. **P-3:** the payoff driver proves only with the clause; both fail-loud negatives (scalar-outside
   rejected; region-outside fails the invariant); loops without the clause byte-identical; IR 1.2
   round-trips — **[PROVE / PROVE-neg ×2 / byte-diff]**.
5. **P-4:** label + `\at` read-back proves; undeclared label rejected — **[PROVE / PROVE-neg]**.
6. **os proves at its standing count, formal_0001 18/18, doc-coherency green, TCB ledger unchanged
   or shrunk — after every item** — **[standing gate]**.
7. `ir.md` is updated for 1.2 (and later 1.3) with the compatibility table; `validate_ir` widens
   `ACCEPTED_IR_VERSIONS` accordingly — **[doc / inspect]**.

> **In one line:** the P-series is the C front-end's exact core bill of materials, each item a
> *platform* change landed in PyCSL under PyCSL's own gates before the CCSL phase that consumes it —
> **P-1** typed binders with ACSL's `integer` (grammar + emitter, zero IR change, first and
> cheapest), **P-4** arbitrary `\at`/`Label` lowering in Module 6 (probe first; supplies
> `LoopEntry`), **P-3** `loop assigns` as an IR-1.2 field whose Module 6 encoding is both obligation
> and payoff (scalar writes checked against the clause, region complements preserved via
> `LoopEntry` — fail-loud on either violation, byte-identical when absent), and **P-2** the
> borrow-shaped mutable-reference model (design-now/implement-last; the seq/ref/view shape
> generalized through its own probe-gated spec, serving C out-params, Rust `&mut`, and Go alike) —
> with the reliefs recorded so the core footprint stays provably "these four and nothing else."
