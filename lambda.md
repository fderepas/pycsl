# lambda.md — Lambda / higher-order support in PyCSL: current state, limitations, and how to go deeper

> **Purpose.** A self-contained briefing on where PyCSL stands on lambdas and
> higher-order functions, why the current limitations exist (root causes, not
> just symptoms), how they compare to the state of the art in deductive
> verification, and concrete directions for a deep dive. Every claim below is
> either a code anchor or a *measured* probe (run on 2026-07-01 against the
> current `main`). Nothing here is aspirational unless explicitly marked "future".
>
> **Audience.** A reviewer who wants to confront PyCSL's design to the literature
> and decide where to invest. No PyCSL-internal knowledge assumed; terms are
> defined on first use.

---

## 0. TL;DR — what works, what doesn't (measured)

PyCSL has **two** lambda representations that are deliberately kept separate:
the **tool** (the Python→WhyML transpiler you actually run) and the **formal
model** (the Rocq+Lean mechanized semantics that proves the WP calculus sound).
They support *different* things.

| Capability | Tool (`pycsl`) | Formal model (Rocq/Lean) | Evidence |
|---|:---:|:---:|---|
| Bind a lambda to a name, then call it | ✅ | ✅ | corpus `0242` |
| Multiple parameters (`lambda a,b: …`) | ✅ (n-ary) | ✅ (via currying) | corpus `0243` |
| Capture an outer variable (lexical) | ✅ | ✅ | corpus `0745`; `test_lambda_lexical_capture` |
| Prove exact-value / inequality contracts through a call | ✅ | ✅ | probe `inc; ensures \result==x+1` → SUCCESS |
| Non-vacuous VCs (false postcondition rejected) | ✅ | — | probe `ensures \result<x` → FAILED |
| **Pass a lambda as a function argument** | ❌ | ❌ | probe `apply1(inc,x)` → FAILED |
| **Return a lambda (function-typed value)** | ❌ | ❌ | probe `return lambda a: a+k` → FAILED |
| **Recursive / self-referential lambda** | ❌ | ❌ | probe `f = lambda a: … f(a-1)` → FAILED |
| **Quantify over functions in contracts** (`\forall f …`) | ❌ | ❌ | not in the contract grammar |
| **Inline lambda as a sub-expression** (`g(lambda a: …)`) | partial† | ❌ | †only where the callee is inlinable |

**One-line summary.** PyCSL supports a **first-order, name-bound, non-escaping,
non-recursive** lambda: you may define a closure, capture values into it, and
call it — and the verifier reasons about the *result*. It does **not** support
lambdas as *values that flow* (passed, returned, stored, recursive) or
higher-order *specifications*. That is the frontier this document maps.

---

## 1. What exists today

### 1.1 The tool: lambda → WhyML `fun`

The Python front-end parses `lambda a, b: e` into an IR node
`{"type":"Lambda","params":[…],"body":…}` (`src/pycsl/frontend/Module5_IREmitter.py`,
`_py_expr_lambda`). Module 6 lowers it to a **first-class WhyML anonymous
function** (`src/pycsl/module6_whyml/expressions.py`, `_handle_lambda_expr`;
documented in `test-suite/annotations.md §7.5`):

```
f = lambda x, y: x + y          ⟶      fun (x: int) (y: int) -> (x + y)
```

Why3 then discharges the resulting verification conditions (VCs) with SMT. Because
Why3's own logic *has* higher-order `fun` values, a lambda that is bound and then
*called in the same scope* verifies fine — the SMT solver sees the applied body.

### 1.2 The formal model: defunctionalized `SLambda` / `SCall`

The mechanized soundness proof (`src/formal-semantics/{rocq,lean}`) does **not**
use higher-order WhyML values. It uses a **defunctionalized** closure model
(Reynolds' defunctionalization: represent each function by a first-order data
value plus an `apply` relation). Three pieces:

- **Value** `VClosure param body cstate` (`Phase2_State.v`; `State.lean`): a
  reified single-parameter closure carrying its body (`stmt`) and a *snapshot* of
  the defining register state `cstate`.
- **Construction** `SLambda x param body` (`Phase1_AST.v`; `AST.lean`, Phase 8):
  a leaf statement that binds `VClosure param body (current reg_state)` at `x`.
  Its weakest-precondition (WP) arm is `Qn (st[x ↦ VClosure param body st])` —
  a plain state update, exactly like assignment.
- **Application** `SCall r fn arg` (`Phase1_AST.v`; `AST.lean`): if `fn`
  evaluates to `VClosure param body cstate`, its WP is the *behavioural formula*
  `∀ st' v, exec (cstate[param ↦ arg]) body (OReturned st' v) → Qn (st[r ↦ v])`.

These are proved sound inside `pycsl_soundness` (both provers, 0 Admitted / 0
sorry, **0 new axioms**). Reachability and lexical capture are witnessed
constructively (`Tests.v`/`Tests.lean`: `test_lambda_reaches_6`,
`test_lambda_lexical_capture`, both axiom-free). **Key modelling facts:**
- **single parameter** — n-ary lambdas are handled by *currying* in the model;
- **capture by value (snapshot)** — `cstate` is the assoc-list at definition
  time, so reassigning an outer variable later does not change the closure
  (`y=5; f=λa.a+y; y=99; r=f(0) ⟹ r=5`, proved);
- **non-emittable** — `gen (SLambda …) = WSkip`, `is_emittable = False`; the
  closure has no first-order WhyML-subset image, so it is excluded from the
  emitter-correspondence theorem and covered *directly* by `pycsl_soundness`.

### 1.3 The two representations do not align (the LINK-1 boundary)

The tool uses a *native* WhyML `fun` (higher-order, n-ary); the formal model uses
a *defunctionalized* first-order closure (single-param, curried). They are **not**
connected constructor-by-constructor. This is recorded as a **named audited
boundary** — decision *5b* in `src/self-annotate/arm-coverage.md §4`: the tool's
`fun` lowering is treated as a sound lowering of the same abstract construct the
formal model defunctionalizes; full IR alignment (*5a*) is future work. The
byte-diff bridge (LINK 2) is unaffected (SLambda is non-emittable), staying 26/26.

---

## 2. The limitations (root causes, minimal examples, why hard)

Each limitation lists a **minimal failing program** (all measured), the **root
cause**, and **why it is hard** — the last is what a deep dive must attack.

### L1 — Passing a lambda as a function argument (first-class *use*)

```python
def apply1(g, x: int) -> int:      #@ ensures \result >= x
    return g(x)
def test(x: int) -> int:           #@ requires x >= 0 ; ensures \result >= x
    inc = lambda a: a + 1
    return apply1(inc, x)          # → Verification FAILED
```

**Root cause.** `g` is a *parameter of function type*. PyCSL's contract language
and its call-site reasoning have **no way to state what `g` guarantees**. There
is no arrow type `int → int` with an attached specification, so at the call
`g(x)` the verifier knows nothing about the result. The formal model is worse off
still: `SCall`'s WP only fires when `fn` *syntactically evaluates to a
`VClosure`* in the current state; a `VClosure` arriving through a parameter is
opaque (`eval_expr` of a parameter var is not statically a closure).

**Why hard.** You must give function *values* a **specification that travels with
them** (see D1/D3). This is the single most important missing feature; L2 and L4
largely follow from it.

### L2 — Returning a lambda (escape / function-typed values)

```python
def make_adder(k: int):
    return lambda a: a + k         # → Verification FAILED (function-typed return)
```

**Root cause.** The return *value* is a function. PyCSL has no function type in
its type discipline for return positions, and the defunctionalized `VClosure`
that would represent it captures a *snapshot of local state* that conceptually
outlives the frame — an **escaping closure**. The Hoare-style state model
(association list, no heap) cannot express "a value that survives its defining
scope and still refers to captured bindings."

**Why hard.** Escape needs closures to live in a **heap** with framing
(separation logic), or an explicit closure-environment discipline. See D4.

### L3 — Recursion / self-reference

```python
def rec(n: int) -> int:            #@ requires n >= 0 ; ensures \result >= 0
    f = lambda a: a if a <= 0 else f(a - 1)   # → FAILED (f not in its own scope)
    return f(n)
```

**Root cause.** In the defunctionalized model `cstate` is the state *before* `f`
is bound, so `f ∉ cstate`: the closure cannot see itself. (Python `lambda` is
anonymous and technically non-recursive too, but the pattern above via a bound
name is what users try.) Even if `f` were in scope, a recursive closure needs a
**variant/termination** argument, which the closure form does not carry.

**Why hard.** Recursion needs either a fixpoint value with a termination measure,
or (more naturally) to route recursion through *named function definitions* with
`decreases`/`\variant` clauses — a different construct than lambda. See D5.

### L4 — Higher-order specifications

There is no way to write a contract that **quantifies over functions**
(`\forall f, is_monotone(f) ⟹ …`) or to hold a **function-valued ghost
variable**. The contract grammar (`contract_expr`) has no function sort;
`eval_contract` is first-order.

**Why hard.** The assertion logic must admit function values and application in
*specifications*, not just in code. Why3's logic can do this; PyCSL's
`contract_expr`/`eval_contract` deliberately cannot (it was kept first-order to
keep `wp_mono`, decidable equality, and the evaluator-axiom boundary small). See D3.

### L5 — Inline lambda as a sub-expression (formal-model shape)

The formal model has **no `ELambda` in `expr`** — closures are only *constructed*
by the `SLambda` *statement* (`f = lambda …`), never inline (`g(lambda a: …)`).

**Root cause / why hard.** Putting `ELambda` in `expr` makes `expr` and `stmt`
**mutually inductive** (a lambda body is a `stmt`). That reopens `eval_expr`
totality, `expr` decidable equality, and `wp_mono` — currently closed proofs.
This was the explicit reason Option 1 (statement-level `SLambda`) was chosen over
Option 2 (`ELambda`) in `phase8-plan.md §2`. See D6.

### L6 — n-ary (tool) vs single-param+currying (formal)

The tool emits n-ary `fun (x)(y) -> e`; the model is single-parameter and treats
`lambda a,b: e` as curried nested `SLambda`. They agree *extensionally* but not
*representationally* — the LINK-1 boundary of §1.3.

### L7 — Capture is snapshot-by-value only

`cstate` is a *copy* of the defining state. There is **no captured *mutable*
reference**: a closure over a variable that is later mutated observes the old
value (proved: L7 is a *feature* for purity, but a *limitation* vs. Python, where
a closure over a `nonlocal`/mutable cell sees updates). PyCSL also forbids the
mutable-cell capture pattern rather than modelling it.

---

## 3. State of the art (how other verifiers handle higher-order)

| System | First-class functions | Spec on function values | Escape/heap closures | Higher-order in specs | Notes |
|---|---|---|---|---|---|
| **Why3 / WhyML** | ✅ native `fun` | via logical functions & `let function` | limited (no GC heap) | ✅ (HO logic) | PyCSL *emits* to this but doesn't exploit HO specs |
| **Dafny** | ✅ arrow types `A ~> B` | ✅ `requires`/`reads`/`ensures` *on the arrow type* | ✅ (heap + `reads` framing) | ✅ | The canonical "spec travels with the function" design |
| **F\*** | ✅ (dependent) | ✅ (refinement/dependent types) | ✅ | ✅ | Effects + monadic reification of closures |
| **Frama-C / ACSL (C)** | function pointers | `\valid_function`, behaviors, `calls` | manual (separation via `\separated`) | limited | Pointer-to-function, not closures |
| **Viper** | ❌ (no first-class fn) | — (encode via predicates) | via predicates + magic wands | encode manually | HO encoded, not primitive |
| **CFML / Separation Logic (Charguéraud)** | ✅ (OCaml closures) | ✅ *characteristic formulae*; a closure satisfies a **spec predicate** | ✅ (SL heap, framing) | ✅ | The reference treatment of *verified higher-order imperative* code |
| **Liquid Haskell** | ✅ | ✅ *abstract refinements* over functions | n/a (pure) | ✅ | Refinements parameterised by predicates |
| **PyCSL (today)** | name-bound, non-escaping | ❌ | ❌ | ❌ | First-order defunctionalized core |

**Where PyCSL sits.** PyCSL's *defunctionalized* core is a sound, minimal
foundation (Reynolds 1972; used in many mechanized semantics precisely because it
keeps everything first-order). The gap to the state of the art is entirely about
**making function values carry specifications** and **letting them flow** —
exactly the step Dafny (arrow types with `requires`/`ensures`) and CFML
(characteristic formulae + a closure *specification predicate*) formalize. Those
two are the most directly transferable precedents.

---

## 4. Deep-dive directions (ranked)

Ranked by *value ÷ risk*. Each: the idea, what it unlocks, precedent, cost/risk.

### D1 — Spec-carrying function values ("closure with a contract") ⭐ highest value
Attach a **pre/postcondition** to a function value: a closure is not just
`VClosure` but `VClosure` **paired with a spec** `(pre : arg → Prop, post : arg →
result → Prop)`, and `SCall`/parameter-typed `g` reason via that spec *instead of*
the body. Callers discharge `pre`, assume `post`.
- **Unlocks:** L1 (passing), and the *specification* half of L2/L4.
- **Precedent:** Dafny arrow types `A ~> B` with `requires`/`ensures`; CFML's
  closure specification predicate `f ⇓ Spec`.
- **Cost/risk:** Medium. Needs a function-type in the contract language and a WP
  rule "call by spec". In the formal model it is *additive* (a new
  `SCall_bySpec` arm) and can reuse `pycsl_soundness` for the closure body when
  the body is available (soundness of the spec = the body refines it).

### D2 — n-ary / currying alignment (LINK-1 *5a*)
Make the IR carry a `LambdaIR`/`CallIR` sum aligning constructor-by-constructor
with `SLambda`/`SCall`; decide n-ary-in-model vs curry-in-tool once.
- **Unlocks:** removes the §1.3 audited boundary; a real LINK-1 for lambda.
- **Precedent:** the Phase-A/B typed-IR migration already did this for other
  constructs.
- **Cost/risk:** Low–Medium, mechanical. Good "warm-up" that also forces the
  n-ary decision needed by D1.

### D3 — Higher-order assertions
Extend `contract_expr`/`eval_contract` with a function sort and application, so
specs can quantify over functions and hold function-valued ghosts.
- **Unlocks:** L4; strengthens D1's specs.
- **Precedent:** Why3's HO logic (already the emission target); F\*, Liquid
  Haskell abstract refinements.
- **Cost/risk:** **High** — reintroduces exactly the first-order simplifications
  (`wp_mono`, decidable equality, evaluator-axiom boundary) that Option 1 avoided.
  Do *after* D1, and probably only in the *contract* plane (not runtime `expr`).

### D4 — Heap-allocated closures + separation-logic framing (escape)
Model escaping closures in a heap with framing, so a returned/stored closure and
its captured environment have a footprint.
- **Unlocks:** L2 (return/store), captured *mutable* state (L7).
- **Precedent:** CFML / Iris-style separation logic for closures; Dafny `reads`.
- **Cost/risk:** **Very high** — needs the deferred typed/store memory model
  (Phase 7 architectural work) *plus* closure environments. Longest path.

### D5 — Recursion via named recursive functions (not lambda)
Route recursion through top-level `def` with `decreases`/`\variant`, giving the
name in-scope in its body and a termination measure — orthogonal to lambda.
- **Unlocks:** L3, and general recursive verified functions.
- **Precedent:** every deductive verifier (Dafny/F\*/Why3 `let rec` + `variant`).
- **Cost/risk:** Medium; a *function-definition* semantics, arguably its own
  phase rather than a lambda feature.

### D6 — `ELambda` as a sub-expression (inline lambdas)
Add `ELambda` to `expr`, accepting `expr`/`stmt` mutual induction, re-proving
totality/decidability/monotonicity (possibly via sized types / well-founded
recursion).
- **Unlocks:** L5 (inline lambdas), full expression-level fidelity to Python.
- **Precedent:** standard in mechanized λ-calculi (mutual induction is routine
  with the right recursion principle).
- **Cost/risk:** High blast radius on *currently-closed* proofs; low conceptual
  novelty. Do only if inline lambdas are demanded by real code.

**Suggested order:** D2 (align, cheap) → **D1 (spec-carrying values, the keystone)**
→ D5 (recursion, independent) → D3 (HO specs) → D4/D6 (heavy, on demand).

---

## 5. A concrete first experiment (smallest step that expands scope)

Pick **D1 restricted to the first-order call-by-spec case**, single parameter:

1. Add a contract-level *function type* `int → int` with `requires`/`ensures`
   (no capture yet), expressible on a function-typed parameter `g`.
2. Formal model: a new WP arm `SCall_bySpec r g arg` =
   `pre(arg) ∧ ∀ v, post(arg, v) → Qn (st[r ↦ v])` — additive, reuses
   `outcome_post`; soundness discharged from the body via the existing
   `pycsl_soundness` when the closure body is known (spec ⊑ body).
3. Corpus: the L1 example (`apply1(inc, x)`) must now **verify**, and a wrong
   spec must **fail** (non-vacuity), mirroring the Phase-8 discipline.
4. Gate: both provers green, 0 new axioms, LINK 2 unchanged.

This is the minimal change that turns "lambda you can call" into "lambda you can
*pass*", which is the doorway to the rest. It is strictly additive (the Phase-6/7/8
playbook) and does not touch `pycsl_soundness`.

---

## 6. Artifacts in this repo (for the deep dive)

- **Plan & decisions:** `phase8-plan.md` (Option analysis, WI list, non-goals),
  `src/self-annotate/arm-coverage.md §4` (LINK-1 decision 5b).
- **Formal model:** `SLambda`/`SCall`/`VClosure` in
  `src/formal-semantics/rocq/{Phase1_AST,Phase2_State,Phase3_SOS,Phase4_WP,Phase5b_Soundness}.v`
  and the Lean mirror `src/formal-semantics/lean/PyCSL/{AST,State,SOS,WP,Soundness}.lean`.
- **Witnesses:** `test_lambda_reaches_6`, `test_lambda_lexical_capture` in
  `Tests.v` / `Tests.lean` (axiom-free).
- **Tool:** `_handle_lambda_expr` (`src/pycsl/module6_whyml/expressions.py`),
  `_py_expr_lambda` (`Module5_IREmitter.py`), `annotations.md §7.5`,
  `docs/pycsl-translational-reference.md §T.6.11` (soundness classification).
- **Corpus:** `test-suite/corpus/pycsl-reference/{0242,0243,0745}.py`
  (single-param, multi-param, capture — all Valid).
- **Status:** `formal-semantics-completion.md §2 Phase 8`;
  `src/formal-semantics/README.md §10 Category A`.

---

## 7. Open questions for the reviewer

1. **Is first-class *use* (D1) in scope for PyCSL's target programs?** If the
   corpus rarely passes/returns functions, the defunctionalized name-bound core
   may already be "enough", and the priority is documentation, not features.
2. **Spec-carrying values vs. inlining.** Would you rather give function values
   contracts (Dafny/CFML style, D1) or aggressively *inline* known closures at
   call sites (no HO reasoning, but only works for statically-known callees)?
3. **How far into the assertion logic (D3)?** Higher-order *specs* are the most
   expressive but the most disruptive to the small-trusted-core design. Is that
   trade-off acceptable, or should specs stay first-order?
4. **Escape (D4) vs. purity.** Do target programs return/store closures, or is
   the non-escaping restriction acceptable (and enforce it as a checked error)?
5. **Recursion (D5) as a separate "verified functions" phase** — agree it's not
   really a *lambda* feature?

These five answers determine whether the next step is a few days (D2 + docs), a
few weeks (D1), or a research programme (D3/D4).
