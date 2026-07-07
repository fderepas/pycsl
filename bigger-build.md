# bigger-build.md — the generalized catamorphism-schema build for the L3 wall

**Status: PLAN of record (execution starts after this file lands).**
**Continues `wall-plan-v2-phase2c-plan.md` (v3). v3's 2-template majority thesis was refuted by the
Phase-0 census (24% coverage); this plan GENERALIZES the schematize idea to a family of catamorphisms
distinguished by result algebra.**

---

## 0. Thesis and what is already banked (verified this session)

**Banked, reused, never re-solved:**
- **L1 — value modeling: SOLVED & CERTIFIED.** Concrete `pydict`/`pyval`/`irkey`/`size`/`wf_ir`/`doc`
  theory in the emitter preamble (on-demand), + axiom-free Rocq 8.20 + Lean 4.29 certificates
  (`Print Assumptions` = "Closed under the global context"; `#print axioms` = kernel-only). **3-axiom
  ledger held.** `compute_in_goal` + interned keys clear the SMT pathologies on both provers.
- **L2 — target-shape provability: SOLVED (both provers).** `v2_iter_mutate_spike.mlw` (walk+mutate,
  `size`-variant, by-ref frame) and `v2_listdict_recurse_spike.mlw` (read+build via `doc` fold).
- **v3 Phase-0 census: 541 IR-reading `\trusted` methods**, classified; placement **feasible** (a
  Module-5-entry AST pass before the `frontend/Module5_IREmitter.py:1477` tuple-target erasure;
  `Module4` was dropped, so there is no earlier semantic pass). Baseline green at 34/34, count 1248.

**The generalization (the verified insight that drives this plan):** the residual is a **family of IR
catamorphisms** — structural folds over the `pyval`/`pydict` inductive value — **distinguished only by
their result algebra** (what the fold accumulates). `walk`/`walk_dict`/`walk_list` is the *type-derived*
recursion skeleton (SYB/uniplate/Equations-style); the result algebra is the small varying part. So we
build **one recognizer + one `GenericFold` IR node parameterized by result algebra**, and **one template
family per algebra**, each instance **re-proved per-method** by the existing `--fun` pipeline (a template
bug → an unprovable instance, never a false proof → **no new trust**; ledger stays 3).

**Where it gets hard (stated up front):** the two proven algebras (T-A unit+frame, T-B doc/string) need
**no new value model**. The collection-result algebras (build-`Set`/list/dict) each need **faithful
collection-result modeling** — the tier-5 "V2" gap — **co-landed with an axiom-free certificate**. Those
are real per-family features with their own go/no-go, not free template slots.

---

## 1. The result-algebra families (from the verified census)

| family | fold result algebra | census | new value model? | target proven? |
|---|---|--:|---|---|
| **A-unit** (was T-A) | `unit` + by-ref accumulator (`writes {acc}`) | **22** | NO — WL-05b `ref`+`writes` | **YES** (`v2_iter_mutate_spike`) |
| **A-doc** (was T-B) | `string` via `doc`/`DCat` fold | **3** | NO — `doc` ADT (in L1 preamble) | **YES** (`v2_listdict_recurse_spike`) |
| **A-bool** (predicates) | `bool` (any/all over the tree) | **16** | NO — `bool` | spike (§3.1) |
| **A-set** | returned `Set[str]` | ⊂ 259 | **YES** — faithful set-result model + cert | spike |
| **A-list** | returned `list` | ⊂ 259 | **YES** — faithful list-result model + cert | spike |
| **A-dict** | returned `dict` | ⊂ 259 | **YES** — faithful dict-result model + cert | spike |
| accessor-only | (no fold) | **106** | (L1 routing suffices) | n/a — separate track |
| out-of-pattern residual | non-self walks (33), dispatcher fan-out, worklist, … | rest of 410 | — | **stays `TRUSTED(essential)`** |

Coverage is *staged*: A-unit + A-doc + A-bool (~41, proven/tractable, no new model) are the tractable
core; the collection-result families (~259, each a real feature) are the uncertain bulk; accessor-only
(106) is a distinct L1-routing track (no template). The exact A-set/A-list/A-dict split of the 259 is a
**Phase-0′ refinement task** (§3.0) — the census bucketed them as "collection-result builders" without
splitting by result type.

---

## 2. Shared infrastructure (Phase 1 — build once)

- **`GenericFold` IR node**: `{ subject, key_filter, pre_action|step, recursion_sites, result_algebra,
  accumulator|return_slot }`. Recorded at **Module-5 entry (AST-intact)**, before line 1477.
- **Recognizer**: fail-closed AST pattern match (extend the v3 Phase-0 spec per algebra). **Precision over
  recall** — a miss stays `\trusted`; a false fire is impossible. Byte-diff-0 gated (fires on 0/756
  corpus, verified); the poisoned fixture (`wall_v3_phase0/poison_ta.py`) must flip the gate red once; the
  near-miss fixtures must not fire.
- **Templater**: instantiate the type-derived `walk`/`walk_dict`/`walk_list` skeleton, mangled per method,
  with the algebra plugged in and payloads inlined (compile-time defunctionalization — no HOF reaches a
  VC). **Spike-congruence check**: the emitted instance for a benchmark method must be near-identical to
  its proven L2 spike (modulo holes/names) — the cheapest evidence instantiation preserves provability.
- **Self-hosting note**: the recognizer/templater are emitter-side code in the verifiable subset; their
  own methods enter the mirror `\trusted`-and-audited initially (and become candidates for their own
  template later).

---

## 3. Per-family build protocol (each family is independently gated, per-family go/no-go)

For EACH family, in order (§4):
0. **(collection families only) refine the census** — split the 259 into A-set/A-list/A-dict + confirm
   each method's fold algebra against its live body.
1. **Spike the target shape** — hand-write the family's target WhyML (the fold + the result algebra) and
   prove all VCs on **Alt-Ergo AND Z3, no axiom**, with a false twin unproven. (Collection families: the
   spike includes the faithful result-collection model.) A NO-GO here ⇒ the family stays
   `TRUSTED(essential)`, ledgered; do not force.
2. **(new value shape only) co-land the certificate** — axiom-free Rocq 8.20 + Lean 4.29 for the result
   model; assert ledger==3 (`Print Assumptions` / `#print axioms`). If it needs a 4th axiom → HALT the
   family.
3. **Build the template family** + extend the recognizer to the algebra.
4. **Convert** the family's census methods: port verbatim, remove `\trusted`, per-instance `--fun`
   whole-body prove, byte-diff-0, feature-touches-verified-method re-port.
5. **Gate**: ledger==3, byte-diff-0 (+ poisoned control), suite green, mirror parity, count strictly down.
   Per-family stop-loss (two batches <50% clean → stop the family, ledger the rest).

---

## 4. Phase order (highest-confidence first; each phase = its own verification gate)

- **Phase 1 — shared infra + A-unit (the first real −N).** `GenericFold` node + recognizer + templater +
  the A-unit (T-A) template; convert the **22 A-unit methods**. Proven target, no new model → the
  highest-confidence conversion. Acceptance: `find_named_expr_targets` + the other A-unit methods
  whole-body-prove; count 1248 → ≤1226.
  *(Caveats from the census to handle: some A-unit are by-return functional folds needing a 2nd sub-form;
  one is a generator; some payloads call other trusted helpers — honest yield may be < 22.)*
- **Phase 2 — A-doc (3) + A-bool (16).** A-doc reuses the proven `doc` fold. A-bool: spike the `bool`
  (any/all) fold first (§3.1), then convert. No new value model; ~19 methods.
- **Phase 3 — collection-result families (A-set → A-list → A-dict).** The hard bulk. Per family: census
  refinement → spike (incl. the result-collection model) → axiom-free certificate → template → convert.
  Each family its own go/no-go; a family that NO-GOs stays trusted. This is the multi-session core; do NOT
  assume it lands.
- **Phase 4 — LINK-2 honesty + scale-out with stop-loss.** Wire the `VERIFIED(lowering=cata)` ledger tag;
  write the LINK-2 boundary note (type-safety/frame/termination proved; loop↔recursion correspondence is
  schematic — one reviewed transformation — with an optional axiom-free Rocq mini-model equivalence proof
  scheduled, not gated). Scale-out per family in batches of ~10; per-stub ledger
  `VERIFIED(cata) | VERIFIED(direct) | TRUSTED(essential,family) | TRUSTED(stop-loss)`. Contract fuzzing
  wired on whatever stays trusted.

---

## 5. Disciplines / gates (every phase, non-negotiable)

- **Ledger == 3** — `Print Assumptions` (Rocq) / `#print axioms` (Lean) after any certificate change;
  every new value shape is *mechanically certified axiom-free*, never assumed. A family needing a 4th
  axiom HALTS.
- **byte-diff 0** on the 756-program corpus (gated recognizer + a poisoned control that flips it red once).
- **Per-instance re-proof = no new trust** — the templater never enters the TCB; a template bug yields an
  unprovable instance (loud), never a false proof.
- **Measure-before-build per family** — spike the target shape (both provers) BEFORE the emitter work;
  refute projections early.
- **Feature-touches-verified-method** — re-port + re-prove any edited verified mirror method in the same
  commit; a full-file proof (`run-self-annotation-suite.sh`), not just `--fun`+fidelity, is in the gate
  (the masking lesson from the baseline-repair).
- **Single-writer**; independent adversarial review of the two artifacts a wrong-but-coherent author gets
  subtly wrong — the recognizer pattern spec and the template text.
- **I verify every agent claim myself** — re-prove converted methods, re-run byte-diff + the suite +
  the ledger check; a census/claim is not believed on the agent's say-so.

## 6. Honest expectations

- **Tractable core (Phases 1–2, ~41 methods):** A-unit (22, proven) + A-doc (3, proven) + A-bool (16,
  likely) — the realistic near-term −N, minus the A-unit caveats.
- **Uncertain bulk (Phase 3, ~259):** the collection-result families each need a faithful result model +
  certificate; expect per-family go/no-go, some NO-GOs, a measured (not projected) yield.
- **Out of scope:** the 106 accessor-only (a separate L1-routing track, no template) and the ~410−259
  out-of-pattern residual (non-self walks, worklists, dispatchers) stay `TRUSTED(essential)`.
- **The prize is the capability**, not the count: a verifying compiler that emits certified catamorphic
  lowerings for generic IR walks, coupled to the certified `pyval` model — exactly the LINK-3 gap and the
  deferred mechanised heterogeneous-value component.

---

## 7. Execution ledger (updated as phases land)
- [◑] Phase 1 — infra + A-unit (22): **MAKE-OR-BREAK PASSED (commit `c436c9af`)**. GenericFold
  recognizer+node+templater landed (`generic_fold.py`); `find_named_expr_targets` converts via the A-unit
  catamorphism — full-file proof SUCCESS (variant decrease Valid — the 2′c termination obstruction gone),
  count 1248→1247, byte-diff 0 (recognizer inert on 0/756), ledger==3 (allowlist+certs untouched, 0 axiom),
  independently re-verified. **The subsystem works.** 1/22 converted; 21 deferred to per-sub-form
  extensions: ~5 check-walks (unit+`raise`, no accumulator — next A-unit brick), ~5 by-return functional
  folds (`set`/`list` result → A-set/A-list, Phase 3), 1 generator, richer-pre-action by-ref collectors.
- [✗] Phase 1b — A-unit check-walk sub-form: **−0 (verified)**. All 5 candidates (`_sa_walk`, `_gso_walk`,
  `_cp_walk`, `_conc_check_reads`, `_pb_expr`) DEFER — the pre-actions uniformly **reach outside the walk**
  (variable-key context-map lookup `symtab.get(node-key)`, or a sibling `\trusted`-helper call), a distinct
  external-dependency feature, not a template slot. No code landed (would fire on 0 methods).
- [✗] Phase 2 — A-doc benchmark `find_return_type`: **DEFER (verified)**. It does NOT fit the closed A-doc
  shape — it composes TWO sibling predicate walks (`_has_return`/`_has_return_with_value`) as guards, does
  **early-return-in-loop** (short-circuit search, not a `DCat` fold), and joins a **synthetic** `["int"]*n`
  list unrelated to the recursion. **The L2 spike `v2_listdict_recurse_spike.mlw` was an *idealized sketch*,
  not a faithful lowering of the real body** — so benchmark #2's "proven target" was aspirational.
- **VERIFIED SCALING REALITY (the decisive finding):** the v3 census classified by the *outer* walk shape
  (isinstance-dict/walk), but real methods' complexity lives in the **pre-action / composition / control
  flow** — sibling-helper calls, variable-key context lookups, composed multi-algebra folds, short-circuit
  search, value-dependent recursion guards. Both benchmarks past #1 DEFERRED on contact. **The census
  family counts (22 A-unit, 3 A-doc, …) are UPPER BOUNDS that do not survive the real bodies** (same
  over-count as tier-1/tier-5). **Clean template yield ≈ 1** (the uniquely self-contained
  `find_named_expr_targets`). Everything else is **per-method feature work** — a context-map value model, a
  sibling-`val`-interop feature, composed-fold/short-circuit-search algebras — each a bounded but real
  go/no-go, NOT a free template slot.
- **BANKED (the genuine win):** the wall is broken *in practice* — a certified catamorphic lowering that
  emits a proving recursion for a real generic dict-walk, no new trust, no new axiom (count 1248→1247). The
  reusable `GenericFold` infra + the verified L1 certificate + the L1/L2/L3 decomposition stand.
- [ ] Phase 3+ — the collection-result families + the per-method dependency features: a distinct
  multi-session campaign, census-first per family, each measured not projected. NOT session-momentum.
