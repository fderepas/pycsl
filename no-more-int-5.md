# Plan: no-more-int Part 5 — residual tracks + a designed path through frame/aliasing

Standalone successor to `no-more-int-4.md`. Part 3 closed the high-value real-type tracks and the
emitter refactor; Part 4 enumerated the demand-driven backlog. **What is new in Part 5:** the
hardest backlog item — A2b, record-param mutation — is no longer "hard, defer." A focused review of
the frame/aliasing literature against Why3's actual grain (see *Three facts* below) yields a
concrete, opinionated design and a 6-step near-term plan. A second item — A4 (json round-trip) — is
recast from a "string-parsing wall" into an ordinary application of the `axiom_from` bridge. The
rest of the backlog is carried forward unchanged.

Every item still follows the **Gate-A demand-driver discipline** (commit a `# pycsl-expected: FAIL`
driver first, then implement to flip it; full-corpus sweep + emission-identical byte-diff as gates).

## Where we are after Part 3 (all committed + pushed)

| Landed | What it bought |
|---|---|
| **Track 2a** sum types + `match`/`case` (0520/0521) | `#@ datatype`, variant `type_decl`, exhaustiveness via Why3 |
| **A1 T1.1 / T1.2** dict string **values** (ν) + **keys** (κ) | `Dict[int,str]` carries content (0523); distinct runtime string keys provably non-aliasing (0526) |
| **Faithful KeyError** (opt-in `#@ no_exception KeyError`) | `d[k]` missing → proof obligation, not a silent default (0524/0525) |
| **A2a** method calls on a record **param** (0522) | `a.bump(k)` propagates the callee's result/param `ensures` |
| **A2c** field-referencing method `ensures` (0529) | `b.get_x()` propagates `\result == self.x` via a receiver param — unblocks getter stubs |
| **A5a** recursive datatypes, single self-recursive (0527/0528) | `type tree = Leaf \| Node tree tree` + `\variant` termination |
| **Part B** emitter refactor, moves 1, 2, 3a–3e | type-dispatch unified, pre-decl exclusion consolidated, giants split — byte-identical |

The **int collapse** is now ~deliberate-tractability only. The residue is *hard* (frame/aliasing —
A2b), *bridge-shaped* (A4 json, A6 hygiene), *low-value* (A3 itertools), or *benign* (A7 bool/tuple).

---

# PART A — remaining tracks

## A2b — record-param mutation = the frame + aliasing problem — **DESIGNED, not deferred**

### What the question actually is
Python has unrestricted mutable aliasing: `def set(p, v): p.f = v` mutates whatever object the
caller passed, and two names can denote the same object. Why3/WhyML **deliberately forbids aliasing
of mutable data** through a static region/alias-control type system (Filliâtre & Paskevich, ESOP
2013) — and that restriction is *precisely* what keeps its VCs first-order and SMT-friendly.
Faithfully modeling Python's mutate-through-alias semantics therefore means importing a discipline
Why3 intentionally does not have. That is the real research question; it is **not** the open binary
"separation logic vs. ownership" it first appears to be. For PyCSL three facts constrain the choice.

### Three facts that constrain PyCSL's choice
- **Fact 1 — PyCSL already ships dynamic frames.** The existing `assigns` clause (`#@ assigns
  arr[0..n]`, `#@ assigns self._value`) *is* a dynamic frame in the Kassios (FM 2006) sense: a
  first-order specification of the locations a method may mutate. We are not choosing between SL and
  dynamic frames in the abstract — we are **already on the dynamic-frames branch**. The question is
  whether to *extend* it to cope with aliasing or *restrict* the input so aliasing never arises.
  Switching to an SL foundation would mean discarding `assigns` and rebuilding on permission
  accounting — far larger than the framing implies.
- **Fact 2 — PyCSL targets Why3; the proven Python recipe targets Viper.** The closest precedent is
  **Nagini** (Eilers & Müller, CAV 2018), a modular verifier for Python handling arbitrary aliasing.
  It works because Viper has **Implicit Dynamic Frames (IDF)** built into the intermediate language
  (a permission is created when a field is first assigned; methods read/write only locations they
  hold permission for). **Why3 does not have IDF.** Transporting Nagini's approach means either
  re-implementing Viper's permission machinery inside WhyML or switching backends. **Cameleer** — a
  Why3-based tool — found this binding enough that it added a *separate Viper backend* for
  heap-dependent OCaml rather than push heap reasoning through Why3. Strong signal about Why3's grain.
- **Fact 3 — heap reasoning is not PyCSL's value proposition.** The *CSL family's distinctive
  contribution is proof-assistant-sourced, cross-validated specifications (`axiom_from`), not a new
  heap logic. Building separation-logic-in-Why3 to handle arbitrary Python aliasing is exactly the
  generic, multi-year verifier engineering the architecture is designed to *avoid* — the strategic
  trap where the bridge (the actual contribution) sits idle while Viper gets rebuilt inside Why3.

### The recommendation — a four-part position
**Restrict aliasing by default; provide region-based dynamic frames as an explicit escape hatch;
route the genuinely hard (reachability) cases through proof-assistant-imported framing lemmas; never
adopt IDF/SL as the foundation.**

1. **Default memory model — ownership boundary, with Why3's grain.** Default to the discipline Why3
   already enforces: mutable objects are not aliased across method boundaries (the **Creusot** move —
   Denis et al., ICFEM 2022, the family member closest in spirit: ownership + Why3, solving aliasing
   by *not having* aliasing). In Python terms, each mutable object is owned by one reference at a
   time; passing it to a method transfers or stack-borrows that ownership. Code that mutates through
   an alias is **rejected at an ownership-check stage with a clear diagnostic**, not silently
   mis-verified. This preserves full SMT tractability, needs no new heap logic, and keeps `assigns`
   intact — `assigns` becomes the footprint of an *owned region*, exactly what Why3's region system
   already understands. Honest cost: idiomatic mutate-through-alias Python is out of scope by default
   (comfortable for the self-hosting target — pycsl's own source is largely functional AST dataflow;
   a real restriction for arbitrary third-party Python, the same one Creusot/Dafny accept).
2. **Escape hatch — region logic, not separation logic.** Where aliasing is genuinely needed, add an
   explicit region/footprint surface built on **Banerjee–Naumann–Rosenberg region logic** (ECOOP
   2008) — *not* IDF, *not* SL — because region logic stays **first-order** and stays in Why3's
   world: regions are ghost `set loc` values, frame conditions are disjointness side-conditions
   (`R1 ∩ R2 = ∅`) the existing Why3→SMT path discharges. A directive surface like:
   ```python
   #@ region R1 = self.reachable_fields()
   #@ assigns R1
   #@ requires \separated_region(R1, other_region)
   ```
   keeps the dynamic-frames flavor of `assigns`, extends it to named regions, and never introduces
   the separating conjunction. **Accept the reachability wall explicitly:** deep-heap framing over
   linked structures with sharing needs transitive closure, which is not first-order — region logic
   will not discharge it automatically. Which leads to the novel part.
3. **The novel move — framing lemmas as `axiom_from` imports.** The reachability properties region
   logic can't automate ("after this rotation the new spine is disjoint from the detached subtree";
   "this reversal permutes exactly the reachable cells") *can* be proved once, in Rocq or Lean, about
   a specific data structure — where transitive closure and induction over heap shape are natural —
   and imported via `#@ axiom_from rocq` / `#@ axiom_from lean`. The cross-check guarantees the two
   statements agree; the SMT solver uses the imported lemma as a black-box first-order axiom. This is
   the proof-out philosophy applied to framing — and, as far as the literature shows, **novel**:
   nobody has used proof-assistant-imported framing lemmas to cross the first-order reachability wall
   in an SMT-backed verifier. It is also the most natural demonstration that `axiom_from` earns its
   keep on a hard problem, not just textbook GCD.
4. **Never adopt IDF/SL as the foundation.** The temptation to "do it properly" (build IDF to match
   Nagini) means re-implementing Viper inside Why3 (huge, against the grain, the thing Cameleer
   avoided) and buries the bridge under heap-logic engineering. If full IDF expressiveness is ever
   genuinely needed, the right move is the **Cameleer move** — target Viper for *that fragment*, not
   rebuild Viper in Why3.

### Why this is right for PyCSL specifically
Works *with* Why3's region system (preserves SMT tractability); keeps `assigns` (evolution, not
rewrite); matches Creusot (closest family member, same conclusion); confines the unavoidable hard
part (reachability) to the proof assistant via the bridge; does not become a multi-year SL project
competing with Nagini on its own terms. The honest cost — idiomatic aliased-mutation Python out of
scope by default — is a documented, defensible **feature boundary, not a soundness gap**, and the
same cost every successful Why3-targeting verifier accepts.

### Concrete near-term plan (gate each stage; build nothing speculatively)
1. **Specify the ownership discipline precisely** (~1–2 wk design). What "no aliasing across method
   boundaries" means in Python: parameter ownership transfer vs. stack-scoped borrowing; what `self`
   ownership means for methods; how immutable values (which may alias freely and safely) are
   distinguished. Reference points: Creusot's borrow model, Dafny's `modifies` discipline.
2. **Build the ownership/alias checker as a frontend pass** (~3–4 wk). Before WhyML emission, reject
   programs violating the discipline with clear diagnostics — the gatekeeper that lets everything
   downstream stay in Why3's native region system. (Per-program-point alias-graph computation, à la
   the Kotlin-on-Viper approach, is one concrete recipe.) *Driver:* a `# pycsl-expected: FAIL`
   program that mutates through an alias, rejected with the ownership diagnostic; a sibling owned-
   transfer program that verifies.
3. **Keep `assigns` as-is; verify it now means "owned footprint."** Under the discipline the existing
   clauses gain a precise meaning with no syntax change — audit that current `assigns`-using corpus
   files still verify byte-identically (this *is* the regression gate for stage 2).
4. **Prototype one imported framing lemma** (~1–2 wk) — the §3 novelty on the smallest example. Pick
   a small heap-shape property (e.g. a list-reversal permutation lemma), prove it in Rocq **and**
   Lean, cross-check, import via `axiom_from`, verify a Python list-reversal against it. *Driver:* the
   list-reversal file with the permutation `ensures`.
5. **Defer the region-logic escape hatch** (§2 named-region machinery) until a real test case needs
   aliasing ownership can't express. Don't build it speculatively.
6. **Write up the position.** Ownership default + Why3 region system + proof-assistant-imported
   framing lemmas is, as far as the search shows, a new point in the design space; the framing-lemma-
   import idea specifically is worth a paper.

**Risk / verdict:** the design removes the open-ended research risk (no SL foundation to build), but
stages 1–2 are real frontend engineering (an alias/ownership analysis is load-bearing and must have
crisp diagnostics). Pull stage 4 (the imported-framing-lemma prototype) **first** if the goal is to
de-risk the novel claim cheaply — it needs no ownership checker and exercises the bridge directly.

## A4 — json round-trip (`loads(dumps(x)) == x`) — **recast: an `axiom_from` application, not a wall**
Part 4 shelved this as a "string-parsing wall." The reflection corrects that: a round-trip theorem
`decode ∘ encode = id` is **exactly** the kind of statement proved once in Rocq/Lean and imported via
`axiom_from`. So A4 is **not a separate research problem** — it is an application of the bridge to
serialization. The verified-serialization canon (**Narcissus**, Delaware et al., POPL/ICFP 2019;
**EverParse/3D**, Swamy et al.) tells you *how to structure the proof* in the proof assistant; the
bridge handles getting it into PyCSL.
- **Recipe:** prove `decode ∘ encode = id` (under bounded depth) in both provers over a recursive
  `#@ datatype Json = …`; cross-check; import as an axiom on the Python `encode`/`decode` pair; let
  Why3 use it black-box. `JObj` additionally needs A1-residual's `map string json` (nested-map value
  type) — see below.
- **Verdict:** still **default don't-build absent a json-content driver**, but when pulled it is
  *ordinary bridge usage*, not a research effort. It also makes a clean demonstration that the family
  architecture absorbs "known-recipe" problems as routine. Same shape as A2b §3 — both are the bridge
  carrying a proof-assistant lemma across a wall SMT can't climb.

## A1-residual — dict value/key types **beyond `int`/`string`** — partial, highest *feature* value
T1.1/T1.2 threaded ν, κ ∈ {`int`, `string`}. The full target is ν ∈ {`int`, `string`, `array int`,
**nested map**}, so **dict-of-lists** (`Dict[str, List[int]]`) and **dict-of-dicts** still collapse
the value to `int`.
- **Gate / driver:** `Dict[str, List[int]]` with `d[k] = xs` then `len(d[k]) == len(xs)`; then
  `Dict[str, Dict[int,int]]` (nested map — the `JObj` enabler for A4).
- **Risk:** medium — the ν side-map and `None -> <default ν>` arm exist (T1.1); this extends ν's
  domain to `array int` / `map …` and the default to `(Array.make 0 0)` / `(const None)`. Blast
  radius is the dict path; **full dict-corpus sweep is the gate** (not byte-diff).
- **Verdict:** highest practical *feature* value of the residual tracks (composes string+list+dict,
  precondition for A4's `JObj`); first to take if a nested-container driver appears.

## A3 — bounded eager `itertools` — NOT STARTED, low value
Bounded-array under-approximation of the **eager** subset (`chain`/`islice`/`product`/`combinations`);
lazy/infinite (`cycle`/`count`/`repeat`, `yield`) stays **out of scope** (no SMT-tractable stream
model). *Driver:* `len(chain(a, n, b, m)) == n + m` + a membership contract. Low risk, self-contained;
**build only on a concrete driver.**

## A5b/A5c/A5d / A5a-residual — sum-type extensions — build on demand
- **A5b** captures referenced in contracts (per-arm postconditions / a `\match` spec operator).
- **A5c** guarded / nested / or-patterns (`case Some(n) if n > 0`, nested ctors, `A | B`) — parser +
  lowering extension per shape; pattern-match-compilation is settled theory (Maranget), so this is
  engineering, not research.
- **A5d** parametric datatypes (`Option[T]`) — composes with A1's parametric machinery; low priority.
- **A5a-residual** mutually-recursive datatypes (`type a = … with b = …`) — the `with` form in
  `preamble.py::_emit_type_decls`; gated on a mutually-recursive driver (e.g. AST `Expr`/`Stmt`).

## A6 — retire `_coerce_to_int` categories — **(a) DONE; (b) audited-not-yet-needed**
`_coerce_to_int` (`expressions.py`, ~line 119) erased real types (string→hash, array→0, map→0,
tuple→hash, self→abstract-op). Discipline: as each track lands, **remove that track's coercion
category**; end state, it fires only for genuinely-untyped (`Any`) operands.

**Corpus-wide audit (instrument every category, emit all 486 files):** only **`string`→hash fires**
(3 times: `"__"`, `"utf-8"`). `self`, `tuple`, `array`, `map` all fire **0 times**.

- **(a) `self`/record→int — ✅ DONE.** Audit-proven dead (0 fires) now that record params/locals are
  handled by the record-aware dotted-call path (A2a/A2c), so the `self_to_int_<type>` abstract op was
  unreachable. Removed; emission **byte-identical across all 462 emitted `.mlw`** (strictly stronger
  than a pass/fail sweep). Kept deliberately: `array`/`map`→placeholder are **defensive nets** for a
  genuinely-untyped collection flowing where `int` is expected (not erasure of a now-typed value);
  `tuple`/`string`→hash are the benign documented collapses (A7).
- **(b) dict key/value→int erasure — not a `_coerce_to_int` category.** It lives at the dict-set/get
  *call sites*, already guarded post-T1.1/T1.2 (`k = index_expr if κ == "string" else
  _coerce_to_int(...)`); for the remaining int dicts the value/key is already an int expression, so
  `_coerce_to_int` is a pass-through there (hence `map`/array fire 0 at those sites). Removing the
  guarded call is byte-identical but only *defensive-net* removal, not dead-value erasure — **defer**
  until a typed non-int/non-string dict value (A1-residual) actually exercises it.
- **Verdict:** the actionable A6 increment (a) is **landed**; (b) is audited and parked behind
  A1-residual. The collapse surface is now `string`-hash + two defensive collection nets + the A7
  tuple/bool benign pair.

## A7 — residual benign collapses — DOCUMENT ONLY
`bool` as `1/0` and bare `tuple → int` (hash) are rare and benign. No driver should chase these; keep
them listed as *intentional* in the τ-table after the Part-B anchor refresh.

---

# PART B-tail — emitter-refactor remainder (move 4 = A6; move 5 hygiene)
Moves 1, 2, 3a–3e landed byte-identical. **Move 4** (kill dead erasure as types land) *is* A6 above.
**Move 5 — mechanical hygiene:** dead-code / unused-import sweep across the split `module5/` +
`module6_whyml/` packages; **re-point the `file:line` anchors** the no-more-int work cites in skills/
docs (they drift after the move-3 extraction — `bin/doc-coherency.py --check` + grep SKILLs for stale
`expressions.py:NNN` / `statements.py:NNN` / `Module5_IREmitter.py:NNN`); consistent naming for the
move-1 type-kind vocabulary. **Gate (every move):** full sweep zero delta; byte-diff a structural
sample; `bin/doc-coherency.py --check` green; one concern per commit, no behavior folded in; confirm
whether `src/self-annotate/src/` (the mirror) must track it (`bin/check-self-annotate-sync.sh`).

---

## Suggested order (by leverage)
1. **A6 / Part-B move 4 — retire superseded `_coerce_to_int` categories.** No driver, sweep-gated,
   shrinks the collapse surface. Available today.
2. **Part-B move 5 — hygiene + anchor refresh.** Cheap, keeps docs/skills honest after the move-3 split.
3. **A2b stage 4 — the imported-framing-lemma prototype** (list-reversal permutation lemma via
   `axiom_from`). De-risks the novel claim cheaply, needs no ownership checker, exercises the bridge.
   Equivalently, **A4** if a json driver appears — same bridge shape.
4. **A2b stages 1–2 — ownership discipline + alias checker.** The real frontend engineering; pull
   when arbitrary-mutation Python is genuinely in scope (or for the self-hosting milestone).
5. **A1-residual — nested-container dict values** — if a container-of-container driver appears;
   highest feature value, unlocks A4's `JObj`.
6. **A5b/A5c/A5d, A5a-residual, A3** — each strictly on its own driver. **A7** — document only.

## Critical files (re-derive line numbers by symbol — they drift after Part-B move 3)
`src/pycsl/module6_whyml/functions.py` (the three method-ensures maps) · `expressions.py`
(`_coerce_to_int` ~119, `_resolve_dotted_signature`/`_handle_dotted_call`, dict MapGet/MapSet) ·
`statements.py` (`map_update_some`, dict-set ν/κ coercion, the `assigns`/footprint lowering) ·
`module6_whyml/preamble.py` (`_emit_type_decls` — variant payload, A5a-residual site) ·
`Module5_IREmitter.py` + `module5/` package · `Module4_SemanticAnalyzer.py`
(`dict_value_types`/`dict_key_types`; **A2b's ownership/alias pass would live as a new frontend
stage near here**) · the `axiom_from` / cross-check machinery (A2b §3, A4) — `audit_proof.py`,
`bin/proof2why3-*`, `src/formal-semantics/{rocq,lean}/`.

## References

**Framing & aliasing canon**
- Reynolds. *Separation Logic: A Logic for Shared Mutable Data Structures.* LICS 2002.
- O'Hearn. *Separation Logic.* CACM 62(2), 2019. (Modern overview.)
- Kassios. *Dynamic Frames…* FM 2006.
- Smans, Jacobs, Piessens. *Implicit Dynamic Frames…* ECOOP 2009; TOPLAS 34(1), 2012.
- Parkinson, Summers. *The Relationship Between Separation Logic and Implicit Dynamic Frames.* ESOP
  2011. (SL is first-order-encodable — but the encoding *is* IDF.)
- Banerjee, Naumann, Rosenberg. *Regional Logic for Local Reasoning about Global Invariants.* ECOOP
  2008. (First-order, SMT-oriented framing — the escape-hatch basis.)

**Tools & precedents**
- Müller, Schwerhoff, Summers. *Viper…* VMCAI 2016.
- Eilers, Müller. *Nagini: A Static Verifier for Python.* CAV 2018. (Python via Viper/IDF — the
  direct precedent, and why it doesn't transplant to Why3.)
- Leino. *Dafny…* LPAR 2010. (`modifies`/`reads` framing — closest to `assigns`.)
- Denis, Jourdan, Marché. *Creusot: A Foundry for the Deductive Verification of Rust Programs.* ICFEM
  2022. (Ownership + Why3 — the spiritually closest family member; same conclusion.)
- Filliâtre, Paskevich. *Why3 — Where Programs Meet Provers.* ESOP 2013. (The region/alias-control
  type system at the root of the question.)
- Pereira, Ravara. *Cameleer.* CAV 2021 (+ the GOSPEL→Viper backend). (The Why3 tool that added a
  Viper backend rather than build IDF in Why3.)

**Verified serialization (A4)**
- Delaware et al. *Narcissus: Correct-by-Construction Derivation of Decoders and Encoders from Binary
  Formats.* POPL/ICFP 2019.
- Swamy et al. *EverParse / 3D.* (Verified parser generation.)

**Ownership foundations (if the discipline route is pushed harder)**
- Jung et al. *RustBelt: Securing the Foundations of the Rust Programming Language.* POPL 2018.
