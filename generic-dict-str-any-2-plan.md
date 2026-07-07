# generic-dict-str-any-2-plan.md — plan v2: breaking the wall by computation, not axiomatization

**Status: PLAN for review (not yet executed).**
**Input: `generic-dict-str-any-2.md` (post-experiment problem statement; frozen benchmark in its §8).**
**Supersedes `generic-dict-str-any-plan.md` where the two conflict — the fmap pivot of plan v1 was run
and refuted (§4c of the report); this plan is built on the measured failure surface.**

---

## 0. What the experiment changed, and the new design thesis

Plan v1's Track M rested on "re-back `PDict` with Why3 `fmap`; solver-native select/store clears the
SMT pathologies." The spike refuted that on all three axes: `PDict (fmap string pyval)` is
**strict-positivity-rejected** (does not compile); the abstract `fmap.Fmap`/`set.Fset` axiomatization
**times out on Z3 even for an int-keyed 2-element map** (so "solver-native" was empirically false in
this stack); and `fmap` exposes **no induction principle**, so no `size` measure is definable over it.
Meanwhile the experiment *confirmed* the other half of plan v1: the assoc-list `pyval` is sound,
certifiable, and proves 14/14 laws; F3 (by-ref mutation) discharges cleanly with `ref` + `writes` +
non-aliasing; and the weak contract (§2.3) remains the scope cut that keeps everything below
research-grade.

The measured failures share one signature: **every timeout is a goal that is *computational* on
concrete data** — a bare-miss lookup on a 2-element literal map, a size decrease on a literal nesting —
**being attacked by e-matching over an abstract theory**. The state of the art has a name for the fix:
*don't axiomatize what you can compute, and don't reason about strings when constructors will do.* The
canonical certified dictionary in existence — CompCert's `Maps.PTree` over interned identifiers — is
exactly this shape: a concrete, strictly-positive, first-order datatype, string keys interned to a
scalar type once at the boundary, every map law a *proven* lemma, every concrete lookup discharged by
*evaluation*. This plan transplants that architecture into WhyML under PyCSL's constraints.

**Three design rules govern everything below:**

- **R-A: Concrete data + evaluation, never abstract theories.** The dict stays a strictly-positive
  first-order datatype (the spike's own assoc-list, canonicalized). Concrete goals are discharged by
  Why3's computation transformations (`compute_in_goal` / `compute_specified`) *before* any solver
  sees them — a bare miss on a literal map reduces to `True` by evaluation, on Alt-Ergo *and* Z3,
  because the solver receives a trivial goal. This is solver-independent by construction, which is how
  the both-provers benchmark criterion gets met.
- **R-B: Constructors, not strings.** IR keys are a *finite, schema-known set* (`ir_schema.py`).
  Intern them: a WhyML enum `type irkey = K_type | K_left | K_op | …` with a certified computable
  bijection to the string literals, used only at the boundary. Key equality/disequality becomes
  datatype-constructor reasoning — native to every solver, zero string theory, which removes both the
  Z3 sequence-solver load and Alt-Ergo's string weakness in one move. (CompCert's `ident` interning of
  source names as positives is the 20-year-old precedent.)
- **R-C: Lemmas proven once, instantiated by e-matching; never axioms.** Everything the solvers
  previously had to *discover* (sub-term size decrease, key distinctness, map laws) becomes a lemma
  pack proven by induction in Rocq 8.20 + Lean 4.29 (or in Why3 logic-function land where syntactic
  structural recursion is accepted), exported as *proven* WhyML lemmas through the existing
  formal-semantics seam. `Print Assumptions` / `#print axioms` stays at the 3-axiom ledger; nothing
  new is trusted, only pre-proved.

---

## 1. The encoding (answers to open questions Q1, Q3, Q4)

### D1 — `pydict`: a canonical, strictly-positive concrete map (Q1, Q3)

```whyml
type irkey  = K_type | K_left | K_right | K_op | (* … generated from ir_schema.py … *) 
type pyval  = PInt int | PStr string | PBool bool | PNone
            | PList (list pyval) | PDict pydict
with pydict = DNil | DCons irkey pyval pydict
```

Strictly positive (no arrow, no map in a constructor — the exact §4c-1 rejection is structurally
impossible). `get`, `mem`, `set`, `keys`, `values_seq` are **logic functions** (syntactic structural
termination — the regime that already works). The fmap-style theory (`get_set_same`, `get_set_other`,
extensionality-up-to-canonical-form) is **derived as proven lemmas** over the concrete type, not
imported as axioms — R-C. A ghost well-formedness `canon d` (keys strictly ordered by a fixed
`irkey` order, hence distinct) is maintained as an invariant by construction in the builder; it makes
lookups deterministic and extensionality structural. Module 5 already controls IR construction, so
canonicality is established at the source, and `wf_ir` (§2) subsumes `canon`.

*Why this discharges where fmap timed out:* the miss goal `get d K_z = None` on a literal `d` is
closed by **evaluation** (R-A) in the Why3 strategy before the solver runs; the general laws are
lemma-pack instantiations (R-C); and key disequalities are constructor disequalities (R-B), free in
the datatype theory. Nothing is left for e-matching to search for.

### D2 — key interning and the boundary bijection (Q1, Q3)

A generated module `IrKeys` provides `irkey`, `string_of_key : irkey -> string`,
`key_of_string : string -> option irkey`, with certified lemmas `key_bijection` (computable proof, no
axiom) and the *distinctness pack is free* (constructors). Genuinely dynamic keys (a computed key not
in the schema — rare in Module 6, to be censused) fall back to a `K_dyn string` arm whose reads route
through guarded projections only; if the census shows hot dynamic-key paths, extend the enum from the
measured key set instead. Strings appear in exactly two places: the boundary bijection and F4's
`render` — nowhere in any walker VC.

### D3 — termination: `size` + lemma pack, fuel as the engineered fallback (Q4)

`size : pyval -> int` is a **logic function** (syntactic checker accepts it — measured). The lemma
pack, proven by induction in Rocq/Lean and exported proven (R-C):

```
size_pos        :  forall v. 0 < size v
size_list_mem   :  forall x l. mem x l -> size x < size (PList l)
size_dict_mem   :  forall k v d. binds k v d -> size v < size (PDict d)
```

The **program-form** walk then carries `variant { size v }`, and each decrease VC is a single
instantiation of a pack lemma — one e-matching step with an explicit trigger, not a discovery. If a
walk shape still resists (mutual recursion over `pyval`/`pydict`), the engineered fallback is the
classic **fuel encoding** (CakeML/Dafny style): `let rec walk (v: pyval) (ghost fuel: int)
requires { size v <= fuel } variant { fuel }` — the variant VC becomes `fuel-1 < fuel` (trivial LIA),
and the pack lemma moves into the precondition instantiation. Both forms stand on the same lemma pack;
fuel merely relocates where it is used. The spike's pair-nested termination VC is the frozen test for
this package.

### D4 — strategy engineering: computation before solvers (Q3)

PyCSL owns its Why3 session, so install a fixed per-goal strategy:
`compute_in_goal` (evaluate lookups/size on literals) → `split_vc` → best-of {Alt-Ergo, Z3, CVC5}
within the existing per-goal budget. Add trigger annotations on the pack lemmas. Guardrail: IR-node
literals are small (schema-bounded fan-out), so evaluation blowup is bounded; a Phase-0 probe measures
the worst-case node. This is where "Timeout → Valid on both provers" is actually won: the two
benchmark spike goals should arrive at the solvers already trivial.

---

## 2. F1 + F2 — routing heterogeneity through the pipeline (Q2)

The experiment's sharpest finding is (§4b): the type was never the problem; **the integration was
never built**. F1 is therefore specified here as five emitter routing rules (E1–E5), and F2 is solved
by making projections *flow-guarded by construction*, with schema lemmas only for the unguarded rest.

- **E1 (type routing).** Any expression whose inferred type is `Any` / heterogeneous lowers to
  `pyval` — the `int` default dies for exactly this class. `Dict[str, Any]` lowers to `pydict`;
  `List[Any]` to `list pyval`. Additive by construction: these expressions currently collapse or
  reject, so no existing corpus lowering changes (the byte-diff-0 gate checks, plus a poisoned
  control: one deliberately non-additive routing must turn the gate red once).
- **E2 (subscript/read).** `node["type"]` with a literal schema key lowers to
  `get n K_type`; a computed key routes through `key_of_string`.
- **E3 (occurrence-typed projection — the F2 kill).** Every Python narrowing construct lowers to a
  total match: `isinstance(v, str)` → `match v with PStr s -> … | _ -> …`; un-narrowed heterogeneous
  unpack `(nm, v) = ("tag_int", 0)` types per-slot from the literal (the `_emit_metatype_tags` fix).
  Under the weak contract, a fully guarded walk needs **no schema facts at all**: type-safety through
  the universal type is discharged by exhaustiveness of the match. This is Typed-Racket-style
  occurrence typing transplanted to VC generation, and it is the reason F2's cost collapses.
- **E4 (unguarded reads).** Where Module-6 code reads `node["op"]` *expecting* `str` with no
  `isinstance` guard, the projection precondition `is_PStr (get n K_op)` is discharged from
  `requires wf_ir node` via a per-(shape,key) lemma generated from `ir_schema.py` — the
  Dminor/semantic-subtyping move: "type" = SMT-decided refinement over the universal value, assumed at
  the boundary (allowed by §5 of the report), *preserved* by the walk. `wf_ir` is a recursive logic
  predicate (syntactic termination) whose compositionality lemma
  (`wf_ir (PDict d) ∧ binds k v d ⟹ wf_val k v`) ships in the pack.
- **E5 (by-ref mutation at scale — F3, Q6).** Promote the *proven* minimal example to a routing rule:
  by-ref `Set[str]`/`Dict` parameter → `ref` cell, mutation → store update, `assigns p` →
  `writes {p}`, plus the non-aliasing precondition; emit a clean `PyCSLSemanticError` where aliasing
  cannot be excluded (fail-closed, consistent with the existing rejection discipline). No new
  semantics — this converts the measured "clean rejection" into a lowering. Heavier separation-logic
  machinery (Viper-style permissions) is deliberately *not* imported: the report's own experiment
  shows the light framing suffices for these shapes.

The typed accessor layer from plan v1 (`irx.py`: `ir_kind`, `ir_get_str`, `ir_children`, ~a dozen
functions verified once against `wf_ir`) survives unchanged and remains the surface-area collapse:
after it lands, raw `pydict` reads exist in ~12 places, not ~125. It must be written in the verifiable
Python subset (the self-hosting constraint) — it is deliberately trivial code, so this is a
formality to *check*, not a risk.

---

## 3. F4 — string emission without string theory (Q5)

Adopt the document ADT, with the byte-identity constraint made load-bearing:

```whyml
type doc = DText string | DInt int | DCat doc doc | DNil
(* render : doc -> string — defined once, certified once *)
```

Walker methods build `doc`; only `render` touches strings, and under the weak contract **no walker VC
ever contains a string term** — projections yield `PStr s` payloads that flow into `DText` opaquely.
`render`'s laws (associativity of `DCat` under rendering, `render (DText s) = s`) are proven once in
Rocq/Lean and exported (R-C). The 756-program **byte-diff-0 gate is the acceptance test for `render`
faithfulness**: the `doc`-routed emitter must reproduce the current concatenation semantics exactly;
Python-side, f-string lowering to `DCat` chains is a mechanical rewrite in the mirror + canonical
source. Where a method computes strings *dynamically* in a way `doc` cannot absorb (census will say;
expected rare), it stays `\trusted` and is ledgered — F4 is cleared for the class, not oversold.

---

## 4. Certificates and the trusted surface (Q7)

Every new value shape co-lands, per the coupling rule, as a **positive/nested inductive** with an
axiom-free certificate: `pyval`/`pydict` (the spike already established the assoc-list form is
conservative; the canonicalized form is the same nesting), `irkey` + bijection (computable), the size
and `wf_ir` lemma packs (induction), `doc` + `render` laws. CI asserts the ledger at exactly 3 via
`Print Assumptions` / `#print axioms`.

Answering Q7's sharp edge — *which techniques secretly trust a decision procedure*: SMT **string
theory** would have silently widened the de-facto trusted surface (goals dischargeable only by Z3's
sequence solver concentrate trust in one prover's most complex theory); R-B removes it from every
walker VC. Likewise the abstract `fmap` axiomatization would have made proofs hostage to each
solver's quantifier instantiation heuristics; R-A/R-C replace discovery with evaluation and
pre-proved instantiation. The residual trusted surface after this plan is exactly what it was before:
the 3 ledger axioms — with strictly *less* practical reliance on any single solver's hard theories,
since the strategy closes the computational goals before solvers run and takes best-of-3 on the rest.

---

## 5. Phases, gates, negative controls

- **Phase 0 — encoding spikes against the frozen benchmark (days; go/no-go).** Hand-write (no emitter
  changes) `pydict` + `irkey` + lemma pack + the D4 strategy, and run the two frozen spike goals:
  bare-miss lookup and pair-nested program-form termination, required **Valid on Alt-Ergo AND Z3, no
  new axiom** (benchmark item 1). Probe `compute_in_goal` cost on the largest schema node. Negative
  controls stood up now: the 4 false twins from the original spike must stay unproven over the new
  encoding (the model must still be able to say no), and one poisoned routing for the byte-diff gate.
  **If the miss or the termination VC still times out here, the plan halts** — that would be the
  rigorous NO-GO the report says is equally valuable, and it would justify `TRUSTED(by-design)` for
  the ~125 with a closed question.
- **Phase 1 — certificates + accessor layer.** Rocq 8.20 + Lean 4.29 certificates for
  D1–D3 land with the WhyML theories (coupling rule); `irx.py` written in the subset and verified
  against `wf_ir`; `wf_ir` generator from `ir_schema.py` (schema is code — the generator is a small
  tool with its own fixture test).
- **Phase 2 — routing E1–E5 + the two benchmark methods.** Implement the emitter rules
  (canonical source first, mirror regenerated, suite + mirror-check + byte-diff-0 gates green).
  Acceptance = benchmark item 2, exactly: `find_return_type` (F1/F2 read case) and
  `find_named_expr_targets` (F2+F3 walk+mutate case) **whole-body-prove** under
  `requires True / ensures True / assigns …` within the automatic budget (items 2 and 5).
- **Phase 3 — F4 `doc` + the emission-defect self-verification.** Land `doc`/`render` + certificate;
  re-implement the two known emitter bugs' fixes (multi-`_` duplicate variable; `(str,int)` mistype —
  the latter falls out of E3) and **self-verify them** — converting the report's "the tool cannot
  self-verify its own bug-fixes" into the acceptance criterion, and moving the emission lever's
  honest yield off 0.
- **Phase 4 — scale-out with stop-loss.** Convert the ~125 in ranked batches of ~10 through
  `irx.py` + E1–E5; ledger per stub `CONVERTED | TRUSTED(essential, reason) | TRUSTED(stop-loss)`.
  Stop-loss: two consecutive batches under 50% clean conversion → stop, ledger the rest, close.
  Leaving stubs trusted remains sound; the campaign's honesty discipline is unchanged. For whatever
  stays `TRUSTED`, wire contract fuzzing (CrossHair/Hypothesis against the stub contracts) as a cheap
  author-independent oracle over the assumptions — no TCB reduction, but Squeeze-Loop pressure on the
  residual.

Every phase: 3-axiom ledger asserted in CI; byte-diff-0 on the corpus; mirror parity; disjoint review
on any manual step.

---

## 6. Explicit answers to the report's seven questions

1. **Q1 (universal-value encoding):** concrete canonicalized `pydict` nested inside `pyval` (D1) —
   strictly positive by construction, program-usable measure via D3, dispatch via interned keys (D2).
   The library `fmap` is abandoned on the report's own evidence, not patched.
2. **Q2 (typing through tagless walks):** occurrence-typed emission makes guarded walks
   schema-free (E3); `wf_ir` + per-(shape,key) lemma packs cover unguarded reads (E4); both only ever
   carry typing facts, per the weak contract.
3. **Q3 (a dictionary theory Z3 actually discharges):** none — a dictionary *program*: evaluation for
   concrete goals (D4), proven lemma packs for symbolic ones (R-C), constructor keys for distinctness
   (R-B). The fmap axiomatization is the measured villain; remove it, don't tune it.
4. **Q4 (program-form termination):** logic-function `size` + induction-proven sub-term lemma pack +
   explicit triggers; fuel encoding as the mechanical fallback with a trivial LIA variant.
5. **Q5 (string emission):** yes — `doc` ADT with a single certified `render`; the byte-diff-0 corpus
   gate doubles as `render`'s faithfulness test.
6. **Q6 (F3 at scale):** promote the proven `ref`+`writes`+non-aliasing pattern to routing rule E5
   with fail-closed rejection; skip heavyweight permission logics — the experiment shows they're not
   needed for these shapes.
7. **Q7 (TCB honesty):** everything lands as computable definitions + induction-proven lemmas with
   Rocq+Lean certificates; ledger pinned at 3 in CI; string theory and abstract map axioms are
   *removed* from the trust story rather than added to it.

### Prior-art anchors for this revision
CompCert `Maps.PTree` + `ident` interning (the certified concrete dictionary over interned keys);
Why3 `compute_in_goal`/`compute_specified` (proof by evaluation ahead of SMT); Dafny `decreases` +
lemma-style termination and CakeML-style fuel; Typed Racket occurrence typing / TypeScript narrowing
(E3); Dminor semantic subtyping over a universal datatype with SMT-decided refinements (E4);
Wadler/Leijen document ADTs (F4); Gillian/JaVerT and Nagini/Viper as the heavyweight alternatives
deliberately not imported (E5 rationale).
