# generic-dict-str-any-plan.md — a plan of attack on the `Dict[str, Any]` wall

**Status: PLAN for review (not yet executed).**
**Input: `generic-dict-str-and.md` (branch `ghost-assign-bc6`, `\trusted` = 1240, residual ≈ 141, wall reach ≈ 125).**
**Audience: the verification lead deciding whether to reopen the wall, and under what stop-loss.**

---

## 0. Framing — what this plan is and is not

The report's bottom line stands: the wall is a **semantic ceiling with four coupled faces**, the
census/F-B1/emission probes prove that **no single feature clears it**, and the value-first call to
stop the *marker* campaign at 1240 was correct. This plan does **not** relitigate that. What it does:
it observes that the F-B1 NO-GO refuted one specific architecture — *"one `pyval` type, ported
walkers as-is, whole-body proof in one step"* — and that the state of the art in dynamic-language
verification never uses that architecture. Every system that has made `Dict[str, Any]`-shaped code
tractable (Nagini/Viper for Python, Gillian/JaVerT for JavaScript, Dminor's semantic subtyping over a
universal datatype, λπ "The Full Monty" semantics) decomposes the problem differently: a **universal
value type + refinement predicates decided by SMT**, **permissions/frames for by-ref mutation**, and
**abstraction layers so the raw dynamic value is touched in exactly one small, verified place**.

The plan therefore attacks the wall on two tracks that converge:

- **Track R (refactor)** — change the *reflection style* of the code, not the logic. The report's own
  key insight (SKILL §10.3: *the convertibility axis is reflection style, not node kind*) cuts both
  ways: style is a **property of the source, and PyCSL owns its source**. Every generic walker that
  can be rewritten as tag-dispatch or routed through a typed accessor layer falls to the
  **already-certified IR-node ADT** — zero new value-model risk.
- **Track M (model)** — for the walkers whose genericity is *essential*, build the value model the
  spike validated (`pyval`), but with the four state-of-the-art corrections that address exactly the
  four F-B1 failure modes: finite-map backing (face 1 + SMT), schema/shape refinement predicates
  (face 2), store-passing/functionalization for by-ref mutation (face 3 / WL-05), and a document ADT
  so emission never touches SMT string theory (face 4).

Constraints inherited unchanged from the campaign discipline: the **3-axiom ledger stays at 3**; every
model extension **co-lands with a Rocq + Lean cross-validated certificate** (the coupling rule, SKILL
§10.5, via the existing `proof2why3` pipeline); a `\trusted` stub is an assumption, never a hole, so
**stopping early is always sound**; and the self-annotation contract remains
`requires True / ensures True / assigns <frame>` — **type-safety + frame, not behavioral content** —
which is precisely what makes Track M feasible at all (§3.4).

---

## 1. Re-reading the F-B1 NO-GO — what was actually refuted

The spike proved more than the report's headline suggests, and the plan leans on the positive part:

| F-B1 result | verdict | what it tells the plan |
|---|---|---|
| `pyval` ADT type-checks, terminates, 14/14 laws on Alt-Ergo **and** Z3, no new axiom | **GO** | the universal-value foundation is sound and certifiable; keep it |
| `find_named_expr_targets` rejected at the emitter on by-ref `Set` mutation | NO-GO **at the emitter** | WL-05 is an *emitter capability gap*, not a semantics wall — WhyML has native `ref`/`writes`; the walker never reached the prover |
| `find_return_type` fails `array int` vs `int` | NO-GO **at the type collapse** | the walker was ported over the *old* `int`-defaulting pipeline, not over `pyval` routing — i.e. the integration layer was never built, only the type |
| string-keyed dispatch times out under the recursive read | NO-GO **at SMT** | known pathology of assoc-list dicts + string theory; the standard fixes (finite maps, key-distinctness lemmas) were not in the spike |
| pair-nested walk's termination VC won't discharge | NO-GO **at SMT** | structural variants on nested `list (string, pyval)` are exactly where a **size measure** (`variant { size v }`) is the textbook replacement |

So the honest restatement is: **the type is proven; the integration (routing, mutation, dispatch
engineering, termination measures) was never attempted.** That is what "breaking the wall" means, and
it is bounded engineering-plus-certificates, not open research — *provided* the goal stays
type-safety + frame (§3.4). The plan's Phase 0 re-runs the exact F-B1 failures as the frozen
benchmark, so success is measured against the same probes that produced the NO-GO.

---

## 2. State of the art — the five techniques this plan imports

1. **Universal datatype + SMT-decided refinements (Dminor / semantic subtyping).** Values live in one
   algebraic type; "types" become *predicates* over it (`wf_ir v`, `is_str (get v "op")`), and the SMT
   solver decides subtyping/shape questions. This is exactly the shape PyCSL needs for tagless walks:
   the walker doesn't dispatch on a tag, but its *precondition* carries a schema predicate from which
   per-key typing facts follow by lemma. Face 2 stops being "no discriminant" and becomes "the
   discriminant is a refinement, not a constructor."
2. **Finite maps over assoc-lists for dict semantics (Why3 `fmap`, solver-native select/store).**
   Assoc-list dicts force recursive reads that string-theory reasoning chokes on (the observed
   timeout). Why3's finite-map theory maps to solver-native array/UF reasoning; iteration order and
   `.values()` walks are recovered through a ghost `bindings : fmap → seq (string, pyval)` view, with
   loop invariants over the processed prefix — the standard Why3 idiom for map iteration.
3. **Functionalization / store-passing for by-ref container mutation (WL-05).** Nagini handles
   mutable Python state via Viper permissions; in WhyML the equivalent low-tech move is to emit by-ref
   `Set`/`Dict` parameters as `ref` cells with `writes` clauses, plus a `\separated`-style
   non-aliasing precondition (the emitter's callers demonstrably don't alias these). Mutation becomes
   store update; `assigns targets` maps to `writes { targets }`. This is an **emitter feature**
   (a fifth routing rule), not a new logic.
4. **Pretty-printing as an ADT (Wadler-style `doc`) so emission never enters SMT string theory.**
   Face 4 couples value-reading to string-building; the fix is to make emitter methods build a
   `type doc = DText string | DInt int | DCat doc doc | …` and prove type-safety + frame over `doc`
   construction only. A single `render : doc → string` function owns all string semantics and is
   specified once, certified in Rocq/Lean, and — under the fixed self-annotation contract — never
   needs character-level SMT reasoning in any walker proof.
5. **Occurrence-typing-shaped emission (flow-sensitive projections).** Where Python narrows
   dynamically (`if isinstance(v, str):`, `if "op" in node:`), the emitter should emit the projection
   guarded by the corresponding `pyval` test (`is_PStr v`, `mem "op" node`), so the path condition
   discharges the projection precondition — the Typed Racket / TypeScript-narrowing discipline,
   transplanted to VC generation.

Complementary, non-proof oracle: for whatever remains `\trusted` at the end, wire **contract fuzzing**
(CrossHair/Hypothesis executing the stub contracts against the real bodies) into CI. It reduces zero
TCB but it is a cheap author-independent check that the *assumptions* are not falsified on reachable
inputs — the Squeeze-Loop instinct applied to the residual.

---

## 3. The architecture — one diagram, four faces mapped

```
                    Python source (Module-6 emitter methods)
                           │
        Track R ───────────┤─────────────── Track M
   (style refactor)        │            (essential genericity)
                           ▼
   tag-dispatched     typed accessor        generic walkers
   rewrites      ──►  layer `irx.py`   ──►  over pyval + wf_ir
   (ADT-addressable,  (ir_get_str,          (fmap-backed dicts,
    already certified) ir_kind, ir_children; seq-view iteration,
                       verified ONCE         size-measure variants,
                       against wf_ir)        key-distinctness lemmas)
                           │                        │
                           ▼                        ▼
                     by-ref mutation:        string emission:
                     ref + writes +          doc ADT, render
                     non-aliasing pre        certified once
                     (WL-05 routing)         (never SMT strings)
                           │                        │
                           └────────┬───────────────┘
                                    ▼
                    Rocq + Lean certificates (proof2why3),
                    3-axiom ledger unchanged, seam = #@ proof imports
```

- **Face 1 (heterogeneous typing)** → `pyval` v2: the spike's constructors, `PDict` re-backed by
  `fmap string pyval`; tuple unpacking routed per-slot through projections (kills the `(str,int)`
  mistyping of `_emit_metatype_tags` at the root — the emitter types each slot from the literal, not
  from a single element type).
- **Face 2 (tagless reflection)** → `wf_ir` schema predicates **generated from `ir_schema.py`** (the
  schema already exists as code!) + the accessor layer; generic walks get `requires wf_ir obj` and
  per-key lemmas.
- **Face 3 (by-ref mutation)** → WL-05 routing rule: `ref` + `writes` + non-aliasing precondition.
- **Face 4 (string emission)** → `doc` ADT; `render` certified once.
- **Face 5 (SMT tractability, implicit in §6 of the report)** → fmap select/store instead of
  recursive assoc reads; `size : pyval → int` measure for nested termination VCs (lemmas
  `size_pos`, `size_dict_mem` proven in Rocq+Lean, imported via `#@ proof` — **lemmas, not axioms**;
  ledger untouched); per-keyset **distinctness lemma packs** (`"type" ≠ "left" ∧ …`) generated by a
  tool and discharged once by computation, so dispatch never re-derives string inequalities.

### 3.4 Why the fixed contract makes this tractable

Every hard thing in dynamic-value verification is *behavioral* (what value comes out). The
self-annotation contract asks only *type-safety + frame*. Concretely that means: every projection's
precondition is discharged (no `int`/`string` collapse), every loop has a variant, every mutation is
inside its declared frame. No walker proof ever needs to state *which* string was emitted or *which*
key was found. This is the decisive scope cut — it is why §2's techniques, each standard, compose
into a bounded project here, and it is also why the report's ROI caveat remains true: the payoff is
**coverage of the meta-verification**, and the soundness-*story* payoff requires the joint
formal-semantics Phase-7 pairing (§7).

---

## 4. Track R — refactor before you model (highest ROI per stub)

The census classified walkers by blocker, not by whether their genericity is *essential*. Track R adds
that second axis. A walker's genericity is **incidental** if it walks `obj.values()` or computed keys
merely because the code predates the typed-node ADT; it is **essential** if it must treat unknown
shapes uniformly (true reflection). The two F-B1 probes are likely one of each: `find_return_type`
dispatches over statement kinds it *knows* (incidental — rewrite as exhaustive match over
`node["type"]`, instantly ADT-addressable); `find_named_expr_targets` walks arbitrary expression trees
(essential — Track M).

- **R0 (census′).** Re-classify the ~85 V1 + ~40 V2-behind-façade readers on the
  incidental/essential axis. Expectation to validate, not assume: emitters are schema-driven programs,
  so a large fraction of "generic" walks are incidental. Deliverable: one row per stub, with the
  refactor sketch or the `essential` tag. *(Estimate: this is the same whole-body-census machinery,
  one more column.)*
- **R1 (accessor layer `irx.py`).** A ~dozen-function typed facade over raw IR dicts —
  `ir_kind(node)`, `ir_get_str(node, k)`, `ir_get_list(node, k)`, `ir_children(node)` — each with a
  real contract (`requires wf_ir node ∧ has_key node k …`), verified **once** over `pyval`/`fmap`.
  Then *no other method touches a raw dict*: the wall's surface area collapses from ~125 methods to
  ~12. This is the single most important structural move in the plan — it is how JaVerT/Gillian keep
  dynamic-object reasoning sane (object operations verified once, everything else composes).
- **R2 (incidental rewrites).** Convert incidental walkers to tag-dispatch or accessor calls.
  Canonical-source first (`src/pycsl/`), mirror regenerated (`self-annotate-stub-gen`), both gates
  green (`run-self-annotation-suite.sh`, `self-annotate-mirror-check.sh`), reference corpus green —
  a refactor that changes emitter behavior is a defect, so the 279+ reference tests are the
  behavioral oracle for every R2 commit.
- **R3 (tuple/unpack typing fix).** The `(str,int)` heterogeneous-unpack mistyping is a Module-6
  typing-rule fix (per-slot types from the literal), independent of `pyval`; it also unblocks
  re-proving the two emission-defect fixes (§6). Small, land early.

**Track R risk:** refactoring verified-adjacent code can introduce the very defects the campaign
hunts. Mitigation: reference corpus as oracle + one **poisoned refactor** negative control (a
deliberately behavior-changing rewrite must turn the suite red before the real R2 batch lands).

---

## 5. Track M — the model, in five work packages

- **M1 — `pyval` v2 + certificates.** Constructors per the spike; `PDict (fmap string pyval)`;
  `bindings` ghost view (`seq`); `size` measure + lemma pack; key-distinctness lemma generator
  (input: the key sets actually used by Module-6, harvested mechanically). Rocq + Lean records via
  `proof2why3`; axiom ledger asserted `== 3` in CI. *Exit test:* the spike's 14 laws re-proved on the
  fmap backing, plus the two SMT pathologies from F-B1 (string-keyed dispatch under recursive read;
  pair-nested termination) discharged on the same hardware/budget that failed before.
- **M2 — WL-05 routing (by-ref mutation).** The emitter rule: by-ref `Set[str]`/`Dict` parameter →
  `ref` cell, mutating method → store update, `assigns p` → `writes {p}`, plus the non-aliasing
  precondition and a `PyCSLSemanticError` when aliasing cannot be excluded (fail-closed, consistent
  with the UB-catalog house style). *Exit test:* `find_named_expr_targets` passes the emitter (the
  exact F-B1 rejection) and whole-body-proves under `requires True/ensures True/assigns targets`.
- **M3 — `wf_ir` schema predicates + `irx.py` proofs.** Generate the predicate from `ir_schema.py`;
  prove the accessor layer against it; per-key typing lemmas emitted alongside. This is where face 2
  dies: tagless walks now carry `wf_ir` and project through lemmas. *Exit test:* `find_return_type`
  whole-body-proves — the second F-B1 probe, and the direct refutation of the `array int` vs `int`
  collapse.
- **M4 — `doc` ADT for emission.** The `doc` type + `render`, certified once; emitter string-building
  methods re-typed over `doc`. Under the fixed contract, walker proofs never open `render`.
  *Exit test:* the two emission-defect fixes (duplicate WhyML variable on multi-`_` unpack; the
  `(str,int)` mistype) are re-implemented and **self-verified** — the report's "the tool cannot yet
  self-verify its own bug-fixes" becomes the acceptance criterion, turned green. Honest clean yield of
  the emission lever moves off 0 by construction or the package fails its gate.
- **M5 — scale-out.** Apply M1–M4 routing to the essential-generic set from R0; convert in ranked
  order; ledger one row per stub: `CONVERTED(R) | CONVERTED(M) | TRUSTED(essential-blocked, reason) |
  TRUSTED(stop-loss)`. Contract fuzzing wired for everything left `TRUSTED`.

---

## 6. Phasing, gates, and negative controls

- **Phase 0 — freeze the benchmark, run three cheap spikes (go/no-go).**
  Benchmark = the exact F-B1 artifacts: `find_return_type`, `find_named_expr_targets`,
  `_emit_metatype_tags`, one emission-defect re-port; frozen so success is measured against what
  failed. Spikes, each days-scale: **(a)** fmap-backed `PDict` vs the spike's assoc-list on the
  string-dispatch and termination VCs — if fmap does not clear the SMT pathologies, Track M halts
  (that *would* indicate research-grade, and the report's stop verdict re-applies); **(b)** WL-05
  minimal example through a hand-emitted `ref`+`writes` WhyML — validates M2's target before touching
  the emitter; **(c)** R0 census′ on a 20-stub sample to estimate the incidental fraction — if it
  comes back ≪ expected, Track R shrinks and the plan's ROI must be re-argued.
  **Also: stand up the negative controls** — a poisoned walker (a real type confusion behind a
  `pyval` façade) that must FAIL the pipeline, and the poisoned refactor for Track R. A conversion
  pipeline that has never rejected anything is coherent-and-wrong until shown otherwise.
- **Phase 1 — M1 + R1 + R3.** The foundation package and the accessor layer; certificates co-land;
  ledger check in CI.
- **Phase 2 — M2 + M3.** The two F-B1 probes turn green (or the plan's core claim is refuted and we
  stop with a measured NO-GO v2, which is itself a publishable closure of the wall question).
- **Phase 3 — M4 + the two self-verified bug-fixes.** Emission face; acceptance = the tool
  self-verifies its own fixes.
- **Phase 4 — R2 + M5 scale-out with stop-loss.** Convert in ranked batches of ~10; **stop-loss:**
  if two consecutive batches convert < 50% cleanly (new SMT pathologies, certificate friction), stop,
  ledger the rest `TRUSTED(stop-loss)`, and close — the campaign discipline already established that
  leaving stubs trusted is sound and honest.
- **Every phase:** 3-axiom ledger asserted; mirror + suite + reference-corpus gates green; disjoint
  review on any manual refinement step, per the house rule.

---

## 7. ROI, honestly restated

The report priced the wall as "~125 markers for a multi-obligation research effort." This plan
re-prices it as: **one refactor track that spends no new logic** (Track R, yield = incidental
fraction × ~125, oracle = existing test corpus) **plus one engineering-with-certificates track**
(Track M) whose five packages are each individually validated or killed by a Phase-0/exit-test gate.
The marker count is still not the point. The point is the two things the report itself flags as the
real value: **(i)** the soundness story — `pyval` v2 + `wf_ir` + `doc`, certified and cross-validated,
is precisely the mechanized heterogeneous-value model that formal-semantics **Phase 7** needs, so
Track M should be scheduled *jointly* with it, sharing the certificates rather than duplicating them
(capability and certificate land together, not capability outrunning its certificate); and **(ii)**
the self-verification capability — after M4, PyCSL can self-verify its own emitter bug-fixes, which
converts every *future* emitter defect from "trusted patch" to "proven patch." That capability, not
the 125 markers, is what breaking the wall buys. If Phase 0 kills Track M, Track R alone still
harvests the incidental walkers against the already-certified ADT at near-zero model risk, and the
wall's residual shrinks to its truly essential core — measured, as before, not assumed.

### Pointers
- Benchmark artifacts: `getting-better/tier3/fb1-feasibility-spike.md`, `…/emission-defect-spike-findings.md`, `…/whole-body-census.md`
- Schema source for `wf_ir`: `src/pycsl/ir_schema.py`; accessor layer lands as `src/pycsl/module6_whyml/irx.py` + mirror
- Certificate pipeline: `proof2why3` / `docs/cross-validated-spec-sources.md`; ledger discipline: `config/skills/self-tcb-reduction/SKILL.md` §10–§11
- Memory-model background for WL-05: `docs/memory_model.md` (`hoare` refs vs `typed`/`store`)
- Prior art anchors: Nagini/Viper (Python via permissions); Gillian/JaVerT (parametric dynamic-object verification); Dminor (semantic subtyping over a universal datatype with SMT); λπ "Python: The Full Monty" (universal-value Python semantics); Why3 `fmap`/`seq` theories; Wadler-style document ADTs for printing
