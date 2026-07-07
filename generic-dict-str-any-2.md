# Breaking the `Dict[str, Any]` wall — an open problem for external review

*Self-contained problem statement, 2026-07-07. Prepared for an external programming-languages /
deductive-verification reviewer. No prior PyCSL knowledge assumed.*

---

## 0. What we are asking you

We have a deductive verifier that verifies **itself**, and there is exactly one construct it cannot
verify about its own source: a method that reads a **generic, heterogeneous, dynamically-typed
dictionary** (`Dict[str, Any]`). We have measured — not assumed — that the obvious universal-value
encoding fails, and we can characterise *why* it fails in terms of four independent obstacles and the
exact behaviour of the underlying SMT solvers. **We are not asking whether the wall can be broken; we
are asking which techniques from the state of the art (universal-value semantics, refinement/occurrence
typing, finite-map SMT reasoning, separation-logic framing, sized/measure termination, defunctionalised
pretty-printing) map onto our specific constraints, and in what combination.** §7 lists the concrete
questions; §8 gives a frozen benchmark any proposed solution must clear.

Crucially, our goal is **weaker than full functional verification** (§2.3): we need only **type-safety
+ frame** of the dictionary-reading code, never the *value* it computes. That scope cut is what makes
us believe the problem is bounded engineering-plus-metatheory rather than open research — but the
naive encoding still fails, so we want expert eyes on the encoding.

---

## 1. The system and its self-verification bootstrap (architecture)

**PyCSL** is a deductive verifier for a statically-analysable subset of Python. Pipeline:

```
Python subset ──(Modules 1–5: parse, weave, semantic-analyse, emit IR)──▶ typed IR (dicts)
      │                                                                         │
      │                                              (Module 6: WhyML emitter)  ▼
      └──────────────────────────────────────────────────────────────▶ WhyML program
                                                                              │
                                                          Why3 VC generation  ▼
                                                      Alt-Ergo / Z3 / CVC5  ◀── verification conditions
```

The verifier discharges Hoare-style contracts (`requires`/`ensures`/`assigns`) written as `#@` comments.
Its trusted computing base is pinned by a **3-axiom ledger** mechanised in **Rocq 8.20 and Lean 4.29**
(`alt_ergo_correct`, `trusted_contracts_axiom`, `why3_implements_wp_w`), from which a soundness theorem
(`pycsl_soundness`) is proved. Any extension that introduces a new WhyML value shape must **co-land a
Rocq+Lean certificate** that the shape is sound, keeping the ledger at exactly 3 axioms (the "coupling
rule"). This is non-negotiable: we cannot buy tractability with a new axiom the mechanised metatheory
does not cover.

**The self-verification bootstrap.** Module 6 (the WhyML emitter, ~4 kLOC) is itself written in the
verifiable Python subset. PyCSL verifies a **mirror** of its own emitter: each emitter method is either
**verified** (PyCSL proves it against a contract) or a **`\trusted` stub** (an *assumed* contract). The
campaign goal is to minimise the trusted core. Today ~1248 stubs remain; a measured census shows the
residual is dominated by **~125 methods that read `Dict[str, Any]`** — the wall.

**Why this is uncomfortable, not merely incomplete.** The IR that Module 6 consumes *is* a
`Dict[str, Any]` (Python dicts with string keys and heterogeneous values: ints, strings, bools, lists,
nested dicts). So the construct PyCSL cannot model is the one its own emitter is built to traverse. The
wall therefore sits **inside the meta-verifier's own gate**: we recently discovered that the leak had
been silently *masking un-proven methods that claimed to be verified* — the tool could not, in fact,
verify the part of itself that manipulates the construct it cannot model. This is a genuine
bootstrapping tension, and it is the sharpest reason to want the wall broken.

---

## 2. The exact problem

### 2.1 The code shape
Module 6 methods dispatch on and project out of untyped IR nodes, e.g. (paraphrased):

```python
def _emit(node: Dict[str, Any]) -> str:           # node: {"type": "BinOp", "op": "+", "left": {...}, "right": {...}}
    if node["type"] == "BinOp":
        return f"({self._emit(node['left'])} {node['op']} {self._emit(node['right'])})"
    ...
    for k, v in node.items():                       # generic walk — no static shape
        if isinstance(v, list): ...
```

Values under a key may be `int | str | bool | list[Any] | Dict[str, Any] | None`. Some methods **read by
a statically-known key** (`node["type"]`), some **walk generically** (`for v in node.values()`), some
**mutate a `Set[str]`/`Dict` parameter in place**, and most **build a WhyML *string*** from what they
read.

### 2.2 What already works (do not re-solve this)
The **typed-node** case is solved. We built and certified an IR-node value ADT (a Why3 variant with a
discriminant and per-arm projections, plus a Rocq/Lean record-valued certificate, ledger held at 3).
Code that dispatches on `node["type"]` and projects named fields verifies against it. **The wall is the
complementary case**: *tagless* reads where there is no constructor to dispatch on.

### 2.3 The scope cut that (we think) makes this tractable — READ THIS
The self-annotation contract is **fixed and deliberately weak**:

```
#@ requires True
#@ ensures True
#@ assigns <tight frame>
```

We verify **type-safety** (every projection is well-typed, no `int`/`string` confusion, every access is
in-bounds) **and frame** (the method mutates only its declared footprint) — **never** the *value*
(`ensures \result == <the exact emitted string>`), and never vacuously. Everything genuinely hard about
dynamic-value *functional* verification — proving *which* value flows where — is **out of scope**. A
reviewer used to full functional verification of dynamic languages should recalibrate: we need the
weakest interesting guarantee. The open question is whether the standard encodings can be made to carry
*just* the typing/framing facts cheaply.

---

## 3. The four faces of the wall

A method verifies only if it clears **all four**; most trip at least one.

| face | obstacle | current status |
|---|---|---|
| **F1 heterogeneous typing** | a `Dict[str,Any]` value / a `(str,int)` tuple / a mixed list has no single element type; the emitter defaults it to `int`, so any *string* slot mistypes (`int` vs `string`) | **open — the core wall** |
| **F2 tagless reflection** | generic walks (`for v in node.values()`, computed keys) have no discriminant to project against; contrast F2′ typed dispatch on a known tag, which is solved by the ADT | **open** |
| **F3 by-ref container mutation** | some walkers mutate a `Set[str]`/`Dict` *parameter* in place; needs a caller-visible frame | **SOLVED in isolation** — `ref` + `writes {p}` + a non-aliasing precondition discharges on both provers (see §4d); it is an emitter routing gap, not a semantics wall |
| **F4 string emission** | the emitter turns the dynamic value into a WhyML *string*, coupling value-reading to string-building and (naively) SMT string theory | **open** |

---

## 4. What we tried, and the exact failure modes (measured, both provers)

We ran a controlled feasibility spike (frozen artifacts in §8). Findings, verbatim where useful:

**(a) The universal-value ADT is sound and certifiable — as an assoc-list.**
```
type pyval = PInt int | PStr string | PBool bool | PNone
           | PList (list pyval) | PDict (list (string, pyval))
```
Type-checks; terminates via Why3's **syntactic** structural checker (pure-logic `function`s); **14/14**
read-back / dispatch / generic-walk laws **Valid** (best-of Alt-Ergo ∪ Z3); 4 false twins stay unproven;
**no axiom**. A Rocq/Lean certificate for it is a positive nested inductive and would be conservative and
axiom-free. **So the value *type* is not the problem.**

**(b) A real generic-dict walker still does not whole-body-prove.** Porting an actual Module-6
`.values()`-walker over the `pyval` type fails — not on the type, but on F1 (the surrounding pipeline
still collapses the value to `int`: `array int` vs `int`) and, where it type-checks, on SMT (below). The
*integration* — routing every read through `pyval`, carrying per-key typing facts, a program-usable
termination measure — was never built; only the type was.

**(c) The obvious SMT fix (finite-map backing) is worse, three ways.** We re-backed the dict as
`PDict (fmap string pyval)`:
1. **Strict-positivity rejection.** Why3: *"Constructor `PDict` contains a non strictly positive
   occurrence of type `pyval`"* — `pyval` sits in the codomain of the map's `string -> pyval` arrow. The
   literal design object does not compile.
2. **Key-lookup does not discharge.** A bare miss `pdict_get d "z" = None` (d has keys ≠ "z"):
   **Timeout on Alt-Ergo AND Z3** at `-t 10`. An *int-keyed* control (zero string theory) also **times
   out on Z3** — i.e. the killer is the abstract `fmap.Fmap` / `set.Fset` axiomatisation itself, which Z3
   cannot discharge even for a trivial 2-element map. "fmap = solver-native select/store" is empirically
   false in this stack. (The assoc-list read-*hit* was Valid; the miss and the fmap are the hard cases.)
3. **No termination measure.** `fmap` exposes no induction principle / fold, so no structural
   `size : pyval -> int` is definable over it; and on the assoc-list backing, a **program-form** walk
   with `variant { size v }` **times out on both provers** (only the *logic-function* form passes the
   syntactic checker — but the emitter's walk is program code, not a logic function).

**(d) By-ref mutation (F3) is not a wall.** A minimal `ref`-cell parameter with `writes {p}` and a
non-aliasing precondition proves `requires True / ensures True / assigns p`-shape with **all VCs Valid on
both provers**. F3 is an emitter *capability* gap (currently a clean rejection), independently
convertible.

**(e) Census.** A whole-body feasibility census over the residual: **0 of 98** candidate methods verify
today; ~125 of ~141 residual trusted stubs are behind F1/F2.

**Summary of the failure surface:** the *type* is fine and *certifiable*; **by-ref mutation is solved**;
the open core is **(F1) making heterogeneous values type-check through the whole emitter pipeline**,
**(F2) carrying typing facts through a tagless walk**, **(F4) emitting strings without SMT string
theory**, and underneath all of them **an SMT/termination-tractable dictionary encoding** that Alt-Ergo
*and* Z3 both discharge and that admits a program-usable measure.

---

## 5. Constraints that bound admissible solutions

A proposal must respect all of these (they are why we can't just adopt a heavyweight framework wholesale):

- **Target logic: Why3 → SMT.** Backends are **Alt-Ergo, Z3, CVC5** (we take best-of-N). No interactive
  proof in the emission path; VCs must discharge automatically within a per-goal budget (~seconds).
- **Strict positivity.** WhyML algebraic types reject non-strictly-positive occurrences (kills
  map-in-constructor, §4c-1).
- **Two termination regimes, and only one is usable here.** Why3 accepts (i) *syntactic* structural
  recursion for **logic `function`s**, and (ii) an explicit `variant { … }` for **program `let rec`**.
  The emitter walks are program code ⇒ regime (ii) ⇒ we need a measure whose decrease **SMT can
  discharge** (§4c-3).
- **The 3-axiom ledger is fixed.** No new SMT axiom that isn't discharged, and **any new value shape must
  co-land an axiom-free Rocq 8.20 + Lean 4.29 certificate** (the coupling rule). A solution that needs a
  new trusted axiom is a non-starter unless it is *mechanically certified*, not assumed.
- **Weakest-guarantee scope (§2.3).** type-safety + frame only. Refinements/schemas may be *assumed in
  preconditions* (the caller establishes `wf_ir node`) but the walk itself must only preserve typing.
- **Byte-for-byte output inertia.** The emitter has a 756-program reference corpus; any change to how a
  construct lowers must be **byte-identical** on all existing programs (we gate on this). New capability
  must be *additive*.
- **Self-hosting.** Whatever models the dict must itself be expressible in the verifiable Python subset
  (the emitter that uses it is also verified) — a mild but real reflexivity constraint.

---

## 6. Where the wall sits in the global architecture

PyCSL's soundness story is three links (LINK-1/2/3): **WP↔operational-semantics soundness**, the
**Module-6 encoding** (Python-subset ⇒ WhyML is faithful), and **emitter self-verification** (Module 6
proves its own contracts). The wall is squarely on **LINK-3**: the emitter methods that read `Dict[str,
Any]` are exactly the ones self-verification cannot yet discharge. Breaking the wall would:

1. **Close the LINK-3 gap** for ~125 methods — the emitter would prove type-safety+frame of its own
   dynamic-dict handling instead of assuming it.
2. **Resolve the bootstrap tension** (§1): the value model needed to *verify* the dict-reading emitter is
   the same capability the emitter would need to *emit* for user programs that use `Dict[str, Any]`.
   Solving it once serves both — this is why it is the highest-value open item, independent of raw stub
   count (the stub-count payoff is modest; the *capability* is the prize).
3. Feed the mechanised metatheory: a certified universal-value model is precisely the deferred
   "heterogeneous value" component the Rocq/Lean development needs, so capability and certificate should
   land **together**.

---

## 7. Open questions for the reviewer (candidate SOTA directions in brackets)

We would value pointers on any of these, especially *combinations* that fit §5:

1. **Universal-value encoding for an SMT backend.** What is the right WhyML/Why3 representation of a
   heterogeneous `Dict[str,Any]` that (a) satisfies strict positivity, (b) admits a **program-usable**
   termination measure, and (c) makes **key-lookup + tag-dispatch discharge on both Alt-Ergo and Z3**?
   *[Dminor / semantic subtyping over a universal datatype with SMT-decided refinements; CDuce set-theoretic
   types; the theory of arrays with extensionality vs. `fmap`; combinatory/functional map encodings that
   avoid the `fmap.Fmap` axiomatisation that Z3 chokes on.]*
2. **Carrying typing facts through a tagless walk (F2) under a weak contract.** Given only
   `requires wf_ir node` (a schema predicate we can generate from our IR schema, which exists as code),
   can per-key typing lemmas be made to discharge each projection's precondition cheaply, so a
   `for v in node.values()` walk type-checks without value reasoning?
   *[occurrence typing / flow-sensitive narrowing — Typed Racket, TypeScript; refinement types — LiquidHaskell,
   F*; "type" = SMT-decided predicate over a universal value.]*
3. **A dictionary theory that Z3 actually discharges.** Our finite-map attempt timed out even on a
   2-element int-keyed map (§4c-2). Is there an encoding (functional arrays? explicit key-set +
   distinctness lemma packs discharged once by computation? a decidable fragment?) that keeps membership
   and miss both fast?
   *[theory of arrays / combinator maps; e-matching-friendly triggers; key-distinctness lemma generation.]*
4. **Program-form termination for heterogeneous recursion.** A `size` measure whose decrease SMT accepts
   for a mutually-recursive walk over nested lists/maps of the universal value (§4c-3).
   *[sized types; well-founded/ordinal measures — ACL2, Dafny `decreases`; structural sub-term orders as
   SMT lemmas.]*
5. **Decoupling string emission (F4).** Should the emitter build a **document ADT**
   (`doc = DText string | DCat doc doc | …`) with a single certified `render : doc -> string`, so no
   walker proof ever enters SMT string theory? *[Wadler/Leijen pretty-printing; defunctionalisation.]*
6. **By-ref mutation at scale (F3).** We have a working `ref`+`writes` minimal example; is there a lighter
   or more compositional framing for in-place `Set`/`Dict` parameter mutation with non-aliasing?
   *[separation logic / implicit dynamic frames — Viper, Nagini; Gillian/JaVerT parametric object reasoning;
   store-passing/functionalisation.]*
7. **Keeping the TCB honest.** Any technique that would add an SMT axiom must instead be **mechanically
   certified** in Rocq 8.20 + Lean 4.29 (ledger stays 3). Which of the above compose with a conservative,
   axiom-free certificate, and which secretly require trusting a decision procedure?

---

## 8. Success criteria — the frozen benchmark a solution must clear

Any proposed encoding is evaluated against these exact, reproducible artifacts (spikes committed in
`test-suite/corpus/conformance/spikes/`, feasibility write-ups in `getting-better/tier3/`):

1. **`fb1_fmap_spike.mlw` / `fb1_pyval_spike.mlw`** — the universal-value type + the SMT pathologies
   (bare-miss key lookup; pair-nested termination VC) that must move from **Timeout** to **Valid on both
   Alt-Ergo and Z3**, with **no new axiom**.
2. **Two real emitter methods** must whole-body-prove under `requires True / ensures True / assigns …`:
   - `find_return_type(stmts: List[Dict[str,Any]]) -> str` — the F1/F2 read case (currently `array int`
     vs `int`).
   - `find_named_expr_targets(obj, targets: Set[str])` — the F2+F3 walk+mutate case.
3. **A certificate** (Rocq 8.20 + Lean 4.29) for the new value shape, `Print Assumptions` / `#print
   axioms` showing the **3-axiom ledger unchanged**.
4. **Byte-diff 0** on the 756-program reference corpus (the change is additive; existing lowerings are
   untouched).
5. Discharge within the automatic per-goal budget on Alt-Ergo/Z3/CVC5 (no interactive proof in the path).

A solution that clears (1)–(5) breaks the wall. A rigorous demonstration that **no** encoding can clear
(1) within these constraints is equally valuable — it would close the question and justify leaving the
~125 methods trusted-by-design.

---

## 9. One-paragraph brief for the reviewer

*PyCSL is a self-verifying Why3/SMT-backed deductive verifier for a Python subset. It can prove
**type-safety + frame** (not functional correctness) of almost all of its own WhyML emitter, except the
~125 methods that read a generic heterogeneous `Dict[str, Any]`. A universal-value ADT is sound and
certifiable, and by-reference mutation is solved, but (i) a finite-map backing is strict-positivity–
rejected and its key-lookup times out on Z3 even for a 2-element map, (ii) tagless `.values()` walks
collapse heterogeneous values to `int`, (iii) program-form recursion over the value has no
SMT-dischargeable termination measure, and (iv) string emission drags in SMT string theory. The
constraints are: automatic SMT only (Alt-Ergo/Z3/CVC5), WhyML strict positivity, a program-usable
`variant`, a fixed 3-axiom Rocq/Lean ledger (new value shapes need an axiom-free certificate), and
byte-identical output on an existing corpus. Which combination of universal-value semantics, refinement/
occurrence typing, SMT-friendly map encodings, sized/measure termination, and defunctionalised
pretty-printing breaks this — under a type-safety-only obligation?*

### Reference artifacts
- Internal wall report (four faces, evidence): `generic-dict-str-and.md`
- Feasibility spikes + measured NO-GO: `getting-better/tier3/fb1-feasibility-spike.md`,
  `getting-better/tier3/wall-plan-phase0.md`, `.../emission-defect-spike-findings.md`
- Census: `getting-better/tier3/whole-body-census.md`
- Spike fixtures: `test-suite/corpus/conformance/spikes/fb1_*.mlw`
- Soundness ledger + LINK-1/2/3: `src/formal-semantics/` (Rocq 8.20 + Lean 4.29)
- Self-verification loop + discipline: `config/skills/self-tcb-reduction/SKILL.md`
- Prior-art anchors we have already noted: Nagini/Viper (Python via permissions), Gillian/JaVerT
  (parametric dynamic-object reasoning), Dminor (semantic subtyping over a universal datatype with SMT),
  λπ "Python: The Full Monty" (universal-value Python semantics), Why3 `fmap`/`seq` theories,
  Wadler/Leijen document ADTs.
