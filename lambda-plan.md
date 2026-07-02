# higher-order-decision.md — The full higher-order program for PyCSL (D1–D6), sequenced

**Companion to** `lambda.md` (design-space map: limitations L1–L7, directions D1–D6) and `the-finishable-path.md` / `facing-the-facts.md` (the small-trusted-core self-verification architecture every phase below must respect or explicitly, minimally, and audibly enlarge).

**Status.** *Decision made — build higher-order support, across all six directions.* This supersedes the earlier D1-only scoping of this memo. The plan is now a sequenced program: the additive, high-value directions land first as a spine (Phases 0–3); the three directions that grow the trusted core or reopen closed proofs (D3, D4, D6) are addressed as **gated expansions** (Phases 4–6), each with a named trigger, a named precondition, and an explicit statement of what invariant it costs. "Address all dimensions" does **not** mean "build all six the same way at the same time" — it means every dimension has a defined home in the sequence, a soundness story, and a go condition.

---

## 0. The shape of the program

```
 Phase 0  Guardrails + arity decision         D2(decision)   L6(part)   additive · days
    │
    ▼
 Phase 1  Spec-carrying values / call-by-spec  D1            L1         additive · KEYSTONE
    │  ├───────────────► Phase 3  Recursion via named def   D5   L3     additive · PARALLEL
    ▼
 Phase 2  Full IR alignment, retire 5b         D2(alignment) L6         additive · mechanical
    │
    ▼  ══════════════ GATED EXPANSIONS — evidence-triggered, core-affecting ══════════════
       Phase 4  Escape: heap closures + framing D4   L2, L7-mut
                trigger: targets return/store closures · precond: Phase-7 memory model
                cost: LINK 2 re-established (emittability/model changes)
       Phase 5  Higher-order assertions         D3   L4
                trigger: a target contract must quantify over functions
                precond: explicit decision to enlarge the audited contract logic
                cost: reopens wp_mono / decidable-eq / evaluator-axiom boundary
       Phase 6  Inline ELambda / mutual induct. D6   L5
                trigger: real code needs inline `g(lambda a: …)`
                precond: re-proof budget · cost: reopens expr/stmt closed proofs
```

The spine (0–3) is buildable now under the existing additive discipline. The expansions (4–6) are the ones `lambda.md §4` correctly flags as high/very-high risk; they are sequenced last and pulled in by the demand instrument built in Phase 0, not scheduled speculatively.

---

## 1. Invariants that hold across every phase

Two disciplines govern the whole program; the gates in each phase are instances of them.

**(I1) Additive by default.** Each phase adds constructs/arms without reopening closed proofs. The standing gate for a spine phase is: **both provers green (Rocq + Lean), 0 Admitted / 0 sorry, 0 new axioms, LINK 2 byte-diff unchanged (26/26), non-vacuity preserved.** A spine phase that cannot meet this is mis-scoped.

**(I2) Core growth is a deliberate, isolated, audited event — never drift.** The expansion phases (4–6) *cannot* all honour I1; that is precisely what makes them expansions. Where a phase must enlarge the trusted core or reopen a proof, the plan requires it to (a) be gated behind an explicit decision, (b) enlarge the *minimum* surface, (c) record the enlargement in `arm-coverage.md` / `audit-guide.md`, and (d) state which specific invariant from I1 it relaxes and why. `the-finishable-path.md`'s whole thesis is a small audited core; these phases spend from that budget, so each expenditure is named and bounded.

Two structural facts from `lambda.md` that the whole program leans on:
- **L7 (snapshot capture) is an asset for the spine.** Frozen-constant environments mean spec-carrying closures need no `reads`/framing — the obligation that makes this expensive elsewhere (Dafny `reads`, CFML footprint) is absent *until Phase 4 introduces escape*. The spine is cheap precisely because it forbids escape.
- **D1 does not require D3.** Function-value contracts are first-order (`pre : arg → Prop`, `post : (arg,res) → Prop`); only quantifying over functions needs higher-order logic. This keeps the contract logic first-order through the entire spine and defers all core growth to Phase 5.

---

## 2. Phase 0 — Guardrails + arity decision (D2 decision, part of L6)

**Goal.** Bound the program's blast radius before any reasoning changes, and settle the one D2 choice that D1 forces.

**Build.**
- Front-end/IR detection emitting an explicit **"higher-order value flow unsupported: <shape>"** diagnostic for every shape not yet reachable in the sequence (return/escape → until Phase 4; recursive lambda → routed to Phase 3; inline `ELambda` → until Phase 6; mutable-cell capture → until Phase 4). Front-end only; no soundness impact.
- Make the **arity decision** (n-ary-in-model vs. curry-in-tool). You need the decision now (Phase 1 depends on it); full alignment is Phase 2. Record it in `arm-coverage.md` beside decision 5b.

**Gate.** I1 trivially (front-end only). **Dual purpose:** the diagnostic is also the **demand instrument** — it counts how often real target code trips each shape, and those counts are the triggers for Phases 4–6 (§8).

---

## 3. Phase 1 — Spec-carrying function values / call-by-spec (D1, L1) — the keystone

**Goal.** A function passed as an argument is reasoned about by its spec: caller discharges `pre`, assumes `post`. Single-parameter, non-escaping, snapshot capture.

**Build.**
- *Contract language:* arrow type with first-order pre/post on a function-typed parameter, `g : int ->{ requires P(a); ensures Q(a,\result) } int`. Parse + contract-AST node. First-order `P,Q` only (I2 boundary).
- *Formal (`Phase1_AST.v`/`Phase2_State.v` + Lean):* `VClosure` paired with its spec `(pre,post)`; clean under snapshot capture (§1, L7).
- *WP arm (`Phase4_WP.v` + `pycsl-wp-spec.mlw`):* `SCall_bySpec r g arg` ⟶ `pre(arg) ∧ ∀v. post(arg,v) → Qn (st[r ↦ v])`. Additive; reuses `outcome_post`.
- *Tool (`expressions.py`):* model abstract `g` as Why3 `val g (x:int):int requires{P} ensures{Q}` and reason from the contract — native call-by-spec on the SMT side.

**Soundness (`Phase5b_Soundness.v` + Lean), both cases required.**
- *Body-known* (visible local closure): discharge `spec ⊑ body` from `pycsl_soundness`; the closure refines the spec.
- *Body-unknown* (abstract `g`): the arm is sound conditional on the supplied closure satisfying its spec; the obligation is discharged at the caller supplying the concrete closure (assume-guarantee). **This is the case that delivers L1.**

**Gate (I1) + definition of done.** Beyond the standing gate, the acceptance suite must exercise the **body-unknown** case, or the phase has shipped inlining (Q2 option B), not call-by-spec:
1. **Abstract-`g` PASS** — `apply1(g,x)` verifies with `g` a parameter, no visible body, driven by the spec.
2. **Non-vacuity on the abstract case** — a wrong declared `post` makes the caller FAIL.
3. **Caller obligation** — supplying a closure that violates `g`'s spec is rejected.
4. **Body-known regression** — visible-`inc` still verifies via refinement.
If only (4) passes, it is not D1.

---

## 4. Phase 3 — Recursion via named recursive functions (D5, L3) — parallel to the spine

**Goal.** General recursive verified functions; recursion routed through top-level `def` with a termination measure, *not* through lambda. Orthogonal to the higher-order machinery, so it may proceed in parallel with Phases 1–2.

**Build.**
- *Contract language:* `\variant`/`decreases` clause; the function name in scope in its own body.
- *Formal:* a function-definition semantics with a well-founded termination argument (standard `let rec` + `variant` treatment); the name resolves to itself in `cstate`.
- *Tool:* lower to WhyML `let rec … variant { … }`.

**Soundness / Gate (I1).** Additive: a new definition form + termination obligation; existing arms untouched. Standing gate applies. Non-vacuity: a false `\variant` (non-decreasing) must FAIL.

**Note on priority.** Recursion is broadly needed by systems/filesystem targets independent of any higher-order story, so its corpus value may exceed D1's for the programs actually verified — measure recursion demand the way Phase 0 measures higher-order demand, and let that decide whether Phase 3 leads or trails Phase 1.

---

## 5. Phase 2 — Full IR alignment, retire boundary 5b (D2 alignment, L6)

**Goal.** Align the IR constructor-by-constructor so the tool's arrow-with-spec and formal `SCall_bySpec`/`SLambda` correspond (LINK-1 *5a*), retiring the audited boundary *5b* recorded in `arm-coverage.md §4`.

**Build.** A `LambdaIR`/`CallIR` sum matching the formal constructors, per the arity decision from Phase 0; the Phase-A/B typed-IR migration already did this for other constructs, so it is mechanical.

**Gate (I1).** Additive/mechanical; standing gate applies. **Do not gate the Phase 1 capability on this** — the capability ships on the *decision* (Phase 0); this closes the *representational* gap afterward.

---

## 6. Phase 4 — Escape: heap-allocated closures + framing (D4, L2, mutable L7) — GATED

**Trigger.** The diagnostic (Phase 0) shows target code returning or storing closures. **Precondition.** The deferred **Phase-7 typed/store memory model** exists — D4 cannot be built on the association-list state; a returned closure's captured environment must have a footprint.

**Goal.** Model escaping closures in a heap with separation-logic framing, so a returned/stored closure and its captured environment survive their defining frame. Reuses Phase 1's spec-carrying value — the spec travels into the heap with the closure.

**Build.** Heap-resident `VClosure` with a footprint; `reads`-style framing on the arrow type (now needed — the L7 asset from §1 is *spent* once capture may be mutable/escaping); CFML/Iris-style closure specification predicate over the heap fragment.

**Cost / gate (I2, relaxed).** This is the phase that **re-establishes LINK 2**: once escaping closures interact with the memory model, the emittability/correspondence story (`SLambda` non-emittable, byte-diff 26/26) changes and must be re-proved, not merely preserved. Budget for a LINK re-establishment, not a byte-diff no-op. Longest path in the program; do not start without the memory-model precondition met.

---

## 7. Phase 5 — Higher-order assertions (D3, L4) — GATED, most core-sensitive

**Trigger.** A concrete target contract genuinely must quantify over functions (`\forall f. is_monotone(f) ⟹ …`) or hold a function-valued ghost — not merely "would be elegant." **Precondition.** An explicit, recorded decision to enlarge the audited contract logic, confined to the **contract plane** (not runtime `expr`).

**Goal.** Give `contract_expr`/`eval_contract` a function sort + application so specs are higher-order.

**Cost / gate (I2, relaxed — the expensive relaxation).** This is the direction that directly attacks `the-finishable-path.md`'s core asset: it reopens the first-order simplifications (`wp_mono`, decidable equality, the small evaluator-axiom boundary) that were deliberately kept first-order. Expect this phase to **add to the audited logic** — it may not be "0 new axioms" in the contract-soundness sense; the enlargement must be minimal, recorded in `audit-guide.md`, and justified against a real program. Sequence this **last among 4–6 unless demand forces otherwise**, precisely because it spends the scarcest budget. Keep it out of the spine entirely (§1, I2).

---

## 8. Phase 6 — Inline ELambda / mutual induction (D6, L5) — GATED, highest blast radius

**Trigger.** Real target code demands inline lambdas as sub-expressions (`g(lambda a: …)`) that cannot be lifted to a named binding. **Precondition.** A re-proof budget: adding `ELambda` to `expr` makes `expr`/`stmt` mutually inductive.

**Goal.** Full expression-level fidelity to Python's inline lambdas.

**Cost / gate (I2, relaxed).** This reopens currently-closed proofs — `eval_expr` totality, `expr` decidable equality, `wp_mono` — via mutual induction (the explicit reason Option 1 was chosen over Option 2 in `phase8-plan.md §2`). "0 Admitted" is the **exit** gate here, not an invariant maintained throughout: proofs are temporarily reopened and must be re-closed with the right recursion principle (sized types / well-founded recursion). Low conceptual novelty, high blast radius — build only on genuine demand.

---

## 9. Demand instrumentation ties the gates together

The measurement the spine builds ahead of (2 of 698 corpus files, 0 of 9 verified targets use `lambda`; `rclpy/` empty) means the spine's first exercisers are **tests you author**, not existing programs — budget the corpus as net-new work. More importantly, the Phase-0 diagnostic turns each unsupported shape into a **counter**: rising return/store trips pull in Phase 4; a real quantify-over-functions need pulls in Phase 5; inline-lambda trips pull in Phase 6. The gated phases are thus *evidence-triggered*, which is what keeps "address all dimensions" from becoming "build the three heavy directions speculatively." Re-measure the demand table when the roadmap corpus (e.g. a populated `rclpy/`) lands.

---

## 10. Anchors to commit (blocking the audit trail)

Cited by `lambda.md` but absent from public `main`; commit so decisions and acceptance work are reachable:
- `test-suite/corpus/pycsl-reference/0745.py` — lexical-capture witness.
- `src/self-annotate/arm-coverage.md` — decision *5b* (Phase 2 target) and the Phase-0 arity decision.
- `phase8-plan.md` — the Option-1-vs-2 rationale underpinning Phase 6's cost.

---

## 11. Bottom line

All six directions have a home in one sequence. Phases 0–3 are the **additive spine** — guardrails + arity decision (D2), the spec-carrying call-by-spec keystone (D1, with the body-unknown suite as its real definition of done), recursion via named functions (D5, parallelisable and possibly higher corpus value than D1), and full IR alignment (D2) — all under the standing gate: both provers green, 0 new axioms, LINK 2 unchanged. Phases 4–6 are **gated expansions** that each spend explicitly from the small-trusted-core budget: escape (D4) needs the Phase-7 memory model and re-establishes LINK 2; higher-order assertions (D3) enlarge the audited logic and are the most core-sensitive; inline lambdas (D6) reopen the expr/stmt proofs. Build the spine now, instrument demand with the Phase-0 diagnostic, and let evidence — not ambition — pull the expansions in, each as a deliberate, minimal, audited enlargement rather than drift.
