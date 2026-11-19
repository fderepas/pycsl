# wall-plan-v2-phase2c-plan.md — plan for L3: schematize, don't synthesize

**Status: PLAN for review (not yet executed).**
**Input: `wall-plan-v2-phase2c-stand-alone.md` (L1 solved+certified, L2 proven, L3 = verifying
code-generation; frozen benchmark in its §8).**
**Continues `generic-dict-str-any-2-plan.md`; L1/L2 artifacts are reused, never re-solved.**

---

## 0. The design thesis — the problem is smaller than "synthesis"

The report's §7 reaches for the heavy end of the state of the art — recursion extraction, SyGuS,
deductive synthesis, general imperative→functional transformation. The plan's central claim is that
the measured facts license something far narrower and far more robust: **the L2 target is not a
program to be synthesized; it is a *derived traversal* of the `pyval` datatype — a catamorphism whose
entire shape is determined by the type, not by the source method.** `walk`/`walk_dict`/`walk_list` is
exactly what datatype-generic programming derives mechanically from a datatype definition (SYB /
uniplate's `universe`/`transformBi`, Haskell's derived `Traversable`, Coq Equations' derived
eliminators): one arm per constructor, one helper per nested type, recursion on match-bound sub-terms.
The only parts that vary per source method are two small **payload slots** — the pre-action
(`if obj.get("type")=="NamedExpr": targets.add(...)`) and the key filter (`k == "stmt" → skip`) — plus
the direction of the result (unit+frame, or a `doc` fold).

So L3 decomposes as **recognize → extract payloads → instantiate a fixed template → prove each
instance with the existing pipeline**:

- **No search.** The pattern class is closed and tiny (the census will enumerate it); a deterministic
  recognizer beats SyGuS on precision, auditability, and the byte-diff-0 discipline. Synthesis proper
  is kept only as a named escalation path if the census refutes the closed-class assumption.
- **No new trust.** The template is *not* a verified-compiler pass in the CompCert sense and does not
  need to be: every instantiation is whole-body-proved by Why3 per the normal self-verification
  pipeline. The template's job is merely to make those VCs *always discharge by construction* —
  recursion on structural sub-terms (so the L1 `size` lemma pack closes every `variant` obligation),
  frame threaded uniformly, interned-key reads, `doc` folds for strings. A template bug yields an
  unprovable instance (loud), never a false proof. Ledger untouched.
- **This is how compilers already do it.** The precedent is not "loop-to-recursion in general" but
  **idiom recognition lowered to a certified schema** — vectorizers recognizing `memcpy`, CompCert
  lowering recognized builtins, Dafny/Why3 users hand-writing exactly this walk shape per datatype.
  The novelty here is only that the schema instantiation is emitted by a verifying compiler and
  re-proved per instance.

The four measured defects (§4 of the report) map onto the pass one-to-one: defect 1 (pyval unwired) →
the recognizer routes the walked value to `pyval` (the E1/E2 routing of plan v1, now scoped to gated
methods); defects 2+3 (`while` over opaque iterator; opaque `val` self-call) → the template replaces
the loop and the self-call *jointly* — they are one lowering decision, not two; defect 4 (no
`variant`) → the template carries `variant { size v } / { size_dict d } / { size_list l }` by
construction, closed by the certified lemma pack.

---

## 1. The pass, in four stages (answers Q1, Q2)

### T1 — Recognizer, placed where the information still exists

§3.3-3 is decisive about placement: tuple targets (`for k, v in …`) are erased at IR construction, so
recognizing in Module 6 is fighting the pipeline. Recognize at **semantic-analysis time** (where
static types, `isinstance` narrowings, and tuple targets are intact) and record a dedicated IR node —
`GenericWalk { subject, key_filter, pre_action, recursion_sites, accumulator }` — the standard
high-level-idiom node. Module 6 then emits from the node; nothing downstream re-discovers anything.
This is *additive by construction*: the node exists only when the recognizer fires, and the corpus
datum (0/756 tuple-target `.items()` walks) means it fires on nothing existing — the byte-diff-0 gate
plus one poisoned control (a corpus program edited to match must flip the gate red once) enforce it.

The recognizer's admissible pattern is specified *closed-form and fail-closed* (Q6): subject typed
`Dict[str,Any]`/`Any`-narrowed-to-dict; body statements drawn only from {literal-key skip-guards,
self-recursive calls on the iterated value (and on list items in the `isinstance(obj, list)` arm),
payload actions whose footprint is within the declared frame}; `continue` allowed, `break`/early
`return` from inside the loop not (v1 of the pattern); no mutation of the subject during iteration.
Anything outside the pattern → no fire → the method simply stays `\trusted`, exactly as today. The
recognizer can only *add* verified methods, never lose one.

### T2 — Payload extraction

From the matched source: the key-filter set (interned via L1's `irkey`), the pre-action lowered by the
existing (L1-wired) routing into a statement over `pyval`/`pydict` accessors, the accumulator
parameter mapped to the proven `ref`+`writes` framing, and the result direction (unit+frame vs `doc`
fold). Payloads are first-order and inlined into the instance — **compile-time defunctionalization**:
the template has holes, not higher-order parameters, so no HOF ever reaches a VC (Reynolds'
defunctionalization done statically, which is also what keeps SMT behavior identical to the
hand-proven L2 artifacts).

### T3 — Template instantiation (the emission)

Two template families, matching the two L2-proven spikes:

- **T-A (walk+mutate):** the `let rec walk … with walk_dict … with walk_list …` group, name-mangled
  per source method (`walk__<method>` etc.) to keep one self-contained group per instance. Cost of
  duplication across ~dozens of methods is bounded and buys VC-locality; sharing one generic walker
  across payloads would require higher-order reasoning for zero benefit under the weak contract.
- **T-B (read+build):** recursion over `List[pydict]` with monomorphic constructor-spine accessors and
  a `doc`/`DCat` fold for the result, exactly the `v2_listdict_recurse_spike.mlw` shape.

The instantiated text differs from the proven spike *only in the payload holes and names* — a
deliberate invariant ("**spike-congruence**") that Phase 2 checks mechanically the first time: emit
the instance for the benchmark method, diff it against the L2 spike modulo holes, require
near-identity. That is the cheapest possible evidence that instantiation preserves provability.

### T4 — Per-instance proof

The existing `--fun` pipeline, unchanged: every emitted instance is whole-body-proved (all VCs Valid,
both provers, per-goal budget). This is where the plan's no-new-trust claim is cashed: the template
never enters the TCB because nothing is believed on its say-so.

---

## 2. Termination and framing at synthesis scale (Q4, Q5)

**Q4:** the structural `size`/`size_dict`/`size_list` measures with the certified lemma pack are
sufficient *by construction of the template*: every recursive call in T-A/T-B is on a match-bound
sub-term (`DCons k v rest` → calls on `v` and `rest`), so each decrease VC is a single instantiation
of `size_dict_mem`/`size_list_mem`/`size_pos` — which is precisely what L2 already proved on the real
walkers. Ranking-function synthesis and sized types are not needed because the template *guarantees*
the decrease shape; they would only become relevant if the census (Phase 0) surfaces walkers whose
recursion is not structural (e.g., worklist algorithms) — those stay `\trusted` in v1 and are
ledgered as a distinct family.

**Q5:** the light `ref { }`+`writes { targets }` framing suffices, and not by luck: the walked data is
a *pure inductive value* (`pyval`), so there is nothing it can alias against the one `ref` cell — the
separation obligation is structural, not spatial. Viper-style permissions would buy generality the
pattern class does not contain. The template threads the accumulator uniformly through the group,
identical to the L2-proven artifact.

---

## 3. The LINK-2 honesty question (Q7) — lean on the scope cut, but say so

Under `requires True / ensures True / assigns frame`, the *verification claim* attaches to the emitted
WhyML: it is well-typed, framed, terminating. Soundness of that claim needs no loop≃recursion
equivalence — the report is right. But the *meaning* of the mirror gate ("method X verified") flows
through LINK-2's encoding-faithfulness, and a pattern-gated lowering that replaces a loop with a
recursion is a new lowering whose faithfulness is currently argued, not proved. The plan's position:

1. **Do not gate on equivalence** — it is not required for the weak contract, and requiring it would
   reintroduce research-grade work (full functional verification of the walkers) that the scope cut
   exists to avoid.
2. **Do record the delta honestly:** methods verified via the gate carry a ledger tag
   `VERIFIED(lowering=cata)` distinguishing them from straight-line lowerings, and the phase write-up
   states the LINK-2 status explicitly: *type-safety, frame, and termination of these methods are
   machine-proved; the loop↔recursion correspondence is schematic (one fixed transformation, reviewed),
   not mechanized.*
3. **Offer the cheap upgrade path:** a one-time Rocq mini-model proof that, on the `GenericWalk`
   idiom, the while-lowering and the cata-lowering are observationally equivalent for
   iteration-order-insensitive payloads (which type-safety/frame/termination are, by construction — none
   of the three properties can distinguish iteration orders). Small, axiom-free, certificate-grade;
   schedule it as Phase 4 nice-to-have, not a gate. If it lands, the `cata` tag retires.

This answers Q7 with a discipline rather than a yes/no: the scope cut is sound to lean on *for the
stated claim*, provided the claim's boundary is written down where the AO can see it.

---

## 4. Phases, gates, negative controls

- **Phase 0 — walker-shape census + prerequisite check (cheap; go/no-go).** Classify the ~125
  residual methods into {T-A walk+mutate, T-B read+build, accessor-only (no template needed — L1
  routing suffices), out-of-pattern}. *Gate:* if T-A+T-B+accessor-only cover ≪ the residual, the
  closed-class thesis fails and the escalation path (template families extended, or genuine synthesis)
  must be re-costed before any emitter work. Also: locate exactly where tuple targets die in
  Modules 3–5 (the §3.3-3 erasure) and confirm the `GenericWalk` node can be recorded before that
  point; define the recognizer's fail-closed pattern spec as a reviewable document; stand up the
  negative controls (poisoned corpus program for the byte-diff gate; near-miss fixtures — subject
  mutated during iteration, early `break` — that must NOT fire; the L2 false twins must stay
  unproven over emitted instances).
- **Phase 1 — `GenericWalk` IR node + recognizer.** Semantic-analysis recognition, node recorded,
  Module 6 untouched; corpus gate green (node fires on nothing); recognizer unit-tested against the
  pattern spec and the near-miss fixtures. Self-hosting note: the recognizer and templater are
  emitter-side code in the verifiable subset; their own methods enter the mirror as `\trusted`
  initially — audited, ledgered, and (pleasingly) the templater's dict-reading methods become
  candidates for their *own* template in a later pass.
- **Phase 2 — T-A template + benchmark 1.** Emit `find_named_expr_targets` from the verbatim source;
  check spike-congruence against `v2_iter_mutate_spike.mlw`; whole-body prove within budget
  (benchmark item 1). This phase burns down defects 1–4 in one lowering.
- **Phase 3 — T-B template + benchmark 2.** Same for `find_return_type` against
  `v2_listdict_recurse_spike.mlw` (benchmark item 2), including the `doc` fold path.
- **Phase 4 — LINK-2 note + optional equivalence mini-proof (§3).** Ledger tag wired; phase write-up
  states the claim boundary; Rocq mini-model scheduled if capacity allows.
- **Phase 5 — scale-out with stop-loss.** Convert by census family in batches of ~10;
  per-stub ledger `VERIFIED(lowering=cata) | VERIFIED(direct) | TRUSTED(out-of-pattern, family) |
  TRUSTED(stop-loss)`; stop-loss = two consecutive batches under 50% clean → stop and close, as
  before. Contract fuzzing stays wired on whatever remains `TRUSTED`.

Every phase: ledger == 3 asserted (`Print Assumptions` / `#print axioms`), byte-diff-0 on the 756
corpus, mirror parity, disjoint review of the pattern spec and the template text (the two artifacts a
wrong-but-coherent author would get subtly wrong).

---

## 5. Explicit answers to the report's seven questions

1. **Q1 (recognizing/extracting the recursion):** don't extract — *replace*. The recognizer matches a
   closed idiom at semantic-analysis time (before tuple-target erasure) and records a high-level IR
   node; the recursion comes from a datatype-derived traversal template (SYB/uniplate-style,
   Equations-style derived eliminator), not from transforming the loop. General imperative→functional
   extraction is explicitly rejected as research-grade and unnecessary given the corpus datum.
2. **Q2 (helper synthesis):** helpers are the fixed skeleton of the template — one per nested type
   (`walk`/`walk_dict`/`walk_list`), name-mangled per instance, payloads inlined by compile-time
   defunctionalization. Nothing is searched for; SyGuS/deductive synthesis is the named escalation
   path only if Phase 0 refutes the closed-class assumption.
3. **Q3 (verified-compiler prior art):** the borrowed architecture is *idiom-gated schematic
   lowering + per-instance re-verification* (vectorizer/builtin-recognition style, and the
   translation-validation tradition: prove each output, not the pass), rather than a CompCert-style
   verified transformation — which the no-new-axiom constraint and the per-instance proof pipeline
   make both unnecessary and more expensive than re-proving instances.
4. **Q4 (termination):** structural `size` measures + the certified lemma pack, sufficient by
   template construction; ranking synthesis/sized types deferred to out-of-pattern families if the
   census finds any.
5. **Q5 (framing):** `ref`+`writes` scales because the walked data is pure inductive value — no
   spatial aliasing exists to manage; permissions logics are deliberately not imported.
6. **Q6 (admissibility):** yes, pattern-gated — with the gate specified closed-form, fail-closed,
   tested against near-miss fixtures, and enforced by byte-diff-0 plus a poisoned control. Precision
   over recall: a miss costs nothing (stays trusted); a false fire costs the additivity guarantee.
7. **Q7 (source-equivalence):** not required for the weak-contract claim; leaned on *explicitly* via a
   `lowering=cata` ledger tag and a written LINK-2 boundary statement, with a small optional Rocq
   equivalence proof as the upgrade path that retires the tag.

### Prior-art anchors for this revision
SYB / uniplate / derived `Traversable` (datatype-generic traversal as the template source); Coq
Equations / `Function` (derived structural eliminators); Reynolds defunctionalization (static, via
payload inlining); translation validation (Pnueli; Necula) and per-instance re-proof as the
alternative to a verified pass; idiom recognition in production compilers (vectorizers, CompCert
builtins); Farzan–Nicolet fold synthesis (the escalation path, if ever needed); Dafny/Why3 mutual
`let rec` + `decreases`/`variant` practice for the mutual-group measure discipline.
