# PyCSL Enhancement Proposal: Inductive Predicates

**Status:** Draft / high-level design
**Scope:** Contract-expression language, module-level declarations, static semantics, WhyML lowering, soundness
**Audience:** PyCSL maintainers, contract authors
**Depends on:** `#@ datatype` (sum types); pairs with `#@ lemma` (proofs by induction) and typed quantifiers
**Non-goal:** implementation patches — this specifies *what* must hold, not the diff.

---

## 1. Motivation

PyCSL today expresses "a property of a structure" with a **recursive boolean function** — a
total `def p(x) -> int` returning `0`/`1`, which must terminate (`#@ \variant`) and is therefore
restricted to *decidable, structurally-recursive* properties (e.g. `all_nonneg`). Many important
specification properties are not of that shape:

- **Well-formedness carved out of a looser type.** The collapsed `Json` type admits junk such as
  `JArr(JInt(2), JInt(3))` (a "cons" whose tail is not a spine). There is no clean total function
  that *defines* "is genuine JSON"; the natural definition is a set of inference rules.
- **Relational / non-structural properties.** Reachability in a (possibly cyclic) graph,
  transitive closure, typing judgments, grammar membership, and operational-semantics steps are
  defined as *least fixpoints of inference rules*, not as terminating computations.

Why3 supports exactly this: an **inductive predicate** is a logical relation defined as the least
fixpoint of a list of Horn clauses, with the strict-positivity condition ensuring soundness. It
auto-derives introduction, inversion, and induction principles. This proposal surfaces inductive
predicates in PyCSL so authors can *define* such relations directly, then *prove* properties about
them with `#@ lemma` functions.

## 2. Where inductive predicates sit

PyCSL gains a third "predicate-like" construct, distinct in kind from the existing ones:

| Construct | Kind | Executable? | Termination obligation? | Typical use |
|---|---|---|---|---|
| recursive boolean function (`def p(x)->int`, 0/1) | total function | yes (code **and** contracts) | yes — `#@ \variant` | decidable, structural tests |
| **inductive predicate** (new) | **least-fixpoint relation** | **no (logic only)** | **none** | well-formedness, reachability, typing, grammars |
| coinductive predicate (future) | greatest-fixpoint relation | no | n/a | safety / infinite-object properties |

The crucial contrast with both recursive functions and lemma functions: an inductive predicate
carries **no `\variant` obligation**. It is a relation, not a computation — its meaning is the
least fixpoint, so non-structural and even non-terminating-looking definitions (transitive
closure over a cycle) are well-defined. The price is that it is **not executable** and not, in
general, decidable.

## 3. Surface syntax

A module-level `#@ inductive` directive (sibling of `#@ datatype`) names the predicate, its typed
parameters, and a 4-space-indented body of named **rules** (Horn clauses):

```
ind_def  ::= "#@ inductive" sig ("," sig)* ":"            # >1 sig = mutually inductive
                 rule+
sig      ::= NAME "(" typed_params ")"
rule     ::= "#@ rule" NAME ":" ["forall" binders "."] [premise ("and" premise)* "==>"] conclusion
conclusion ::= NAME "(" args ")"                          # an application of a *defined* predicate
```

Each rule is a universally-closed implication whose **consequent is an application of one of the
predicates being defined**. The defined predicate(s) may appear in premises only **positively**
(§7.1).

**Simple structural predicate:**

```python
#@ inductive even(n: int):
#@     rule even_zero:                      even(0)
#@     rule even_step: forall m: int. even(m) ==> even(m + 2)
```

**Mutually-inductive — well-formed JSON, carving the valid subset out of the collapsed type:**

```python
#@ inductive wf(x: Json), wf_spine(s: Json):
#@     rule wf_null:                                  wf(JNull)
#@     rule wf_bool:  forall b: bool.                 wf(JBool(b))
#@     rule wf_int:   forall n: int.                  wf(JInt(n))
#@     rule wf_str:   forall t: str.                  wf(JStr(t))
#@     rule wf_arr:   forall h: Json, s: Json. wf(h) and wf_spine(s) ==> wf(JArr(h, s))
#@     rule wf_obj:   forall k: str, v: Json, r: Json. wf(v) and wf_obj_spine(r) ==> wf(JObj(k, v, r))
#@     rule sp_nil:                                   wf_spine(JNil)
#@     rule sp_cons:  forall h: Json, s: Json. wf(h) and wf_spine(s) ==> wf_spine(JArr(h, s))
```

Here `wf(JArr(JInt(2), JInt(3)))` is **not derivable** (the tail `JInt(3)` satisfies no
`wf_spine` rule), so the predicate precisely excludes the junk value the type alone admits.

**Relational / non-structural — reachability (cannot be a terminating function):**

```python
#@ inductive reaches(g: Graph, a: int, b: int):
#@     rule reach_refl: forall x: int.                         reaches(g, x, x)
#@     rule reach_step: forall x: int, y: int, z: int. edge(g, x, y) and reaches(g, y, z) ==> reaches(g, x, z)
```

## 4. What an inductive predicate gives you

From the clauses, Why3 derives three principles, all usable in PyCSL contracts and `#@ lemma`
bodies:

- **Introduction** (one per rule): to establish `wf(JArr(h, s))`, prove `wf(h)` and `wf_spine(s)`.
- **Inversion / elimination**: from `wf(x)`, case-split on which rule could have produced it — this
  is how `not wf(JArr(JInt(2), JInt(3)))` is proved.
- **Induction principle**: to prove `\forall x. wf(x) ==> P(x)`, prove `P` for each rule assuming
  it on the recursive premises. This is consumed by a `#@ lemma` function (§6).

## 5. Usage

Inductive predicates are **logic-only**. They may appear in `#@ requires`, `#@ ensures`, loop
invariants, the premises/conclusions of `#@ lemma` functions, and the premises of other inductive
rules. They may **not** be called from executable Python (they have no computational content):

```python
#@ requires wf(x)
#@ ensures \result == json_sum(x)
#@ \variant x
#@ assigns \nothing
def sum_numbers(x: Json) -> int:
    ...
```

If a runtime test of the property is needed, write a separate **recursive boolean function** and
prove the two agree with a lemma — a *reflection* bridge (§9, P4):

```python
#@ lemma
#@ ensures (is_wf(x) == 1) == wf(x)
#@ \variant x
#@ assigns \nothing
def is_wf_correct(x: Json) -> None: ...
```

## 6. Interplay with lemma functions (essential)

SMT backends do not natively understand inductive predicates — Why3 transforms them away per
prover driver, and crucially the solvers will not perform induction on their own. Therefore:

- **Introduction and inversion** generally go through with the solver alone.
- **Any universally-quantified consequence** of an inductive predicate
  (`\forall x. wf(x) ==> P(x)`) requires the **induction principle**, which is *exactly* what a
  recursive `#@ lemma` function supplies (its recursive calls = the IH for each recursive premise).

So the two features are a designed pair: **inductive predicates define the relation; lemma
functions prove theorems about it by induction.** Neither subsumes the other.

## 7. Soundness (mandatory rules)

1. **Strict positivity.** Each defined predicate may occur in rule premises only in *positive*
   position (never under negation, never in the antecedent of a nested implication that flips its
   polarity). This is the soundness lynchpin — it guarantees the defining operator is monotone and
   hence that a least fixpoint exists. Module 4 rejects any non-strictly-positive clause, mirroring
   Why3's own check.
2. **Conclusion shape.** Every rule's consequent must be an application of one of the predicates
   being defined (to argument terms, possibly built with datatype constructors). A rule concluding
   anything else is rejected.
3. **Arity respected.** No partial application of predicates (Why3 forbids it); every predicate
   reference supplies all arguments.
4. **Logic-only / erasure.** Inductive predicates carry no code, are erased at extraction, and may
   not appear in executable position. There is no `\variant` and no termination obligation.
5. **No effects.** Premises may reference only other predicates and **pure** (`assigns \nothing`)
   functions.

## 8. Static semantics & module impact

Well-formedness (Module 4 — Semantic Analyzer): every rule is a closed implication with a
defined-predicate consequent (§7.2); strict positivity holds (§7.1); all binders and argument
terms are well-typed against the declared parameter types; predicate arities are respected; and no
inductive predicate is used in executable position.

| Module | Change |
|---|---|
| **Module 2 — Parser** | parse the `#@ inductive` block (header with one or more sigs, indented `#@ rule` clauses) |
| **Module 3 — Weaver** | register the predicate(s) as module-level logic symbols |
| **Module 4 — Semantic Analyzer** | strict-positivity check; conclusion-shape and arity checks; binder/argument typing; executable-position ban |
| **Module 5 — IR Emitter** (`ir_schema`) | an inductive-predicate node holding the (mutual) clause set |
| **Module 6 — WhyML Transpiler** | emit `inductive p (…) = | Rule : clause … end`, with mutual sets as `inductive p … = … with q … = … end` |

## 9. Lowering to WhyML (Module 6)

```
#@ inductive even(n: int):          ->  inductive even (n: int) =
#@   rule even_zero: even(0)              | Even_zero : even 0
#@   rule even_step:                      | Even_step : forall m: int. even m -> even (m + 2)
#@     forall m. even(m) ==> even(m+2)    end
```

Mutually-inductive predicates lower to a single `inductive … with …` group:

```
inductive wf (x: json) =
    | Wf_null : wf JNull
    | …
    | Wf_arr  : forall h s: json. wf h -> wf_spine s -> wf (JArr h s)
with wf_spine (s: json) =
    | Sp_nil  : wf_spine JNil
    | Sp_cons : forall h s: json. wf h -> wf_spine s -> wf_spine (JArr h s)
end
```

Each PyCSL `rule` becomes one named Why3 clause `RuleName : forall binders. prem1 -> … -> concl`.

## 10. Phasing

| Phase | Delivers | Risk |
|---|---|---|
| **P1 — Single structural predicate** | one `inductive p = …`, usable in contracts; introduction + inversion | low |
| **P2 — Mutually-inductive predicates** | `inductive … with …` groups (e.g. `wf`/`wf_spine`) | medium |
| **P3 — Relational / non-structural** | reachability, transitive closure; universally-quantified consequences discharged via `#@ lemma` induction | medium; depends on lemma functions |
| **P4 — Reflection & coinduction** | executable decision function + agreement lemma; investigate coinductive (greatest-fixpoint) predicates | medium / research |

Each phase ships corpus drivers in the existing numbering style: a PASS, plus FAIL twins — a
**non-strictly-positive** definition (must be rejected as unsound), a derivation attempt for an
excluded value (`wf(JArr(JInt 2, JInt 3))` must be unprovable, and its negation provable by
inversion), and an inductive predicate used illegally in executable code (rejected).

## 11. Validation

- **Positivity gate (critical):** an anti-soundness suite confirms that a clause with the defined
  predicate in a negative position is rejected, demonstrating inductive definitions cannot
  introduce an inconsistent least fixpoint.
- **Carving correctness:** `wf` excludes exactly the junk values the collapsed `Json` type admits;
  a `#@ lemma` proves `wf(x) ==> P(x)` for a representative `P`, and inversion proves
  `not wf(<malformed>)`.
- **Relational demo:** `reaches` over a small cyclic graph proves a reachability fact and refutes a
  non-reachability one — a property no terminating recursive function could define.
- **Erasure check:** inductive predicates and their occurrences disappear under extraction.

## 12. Open questions

1. **Automation ceiling.** Because SMT backends do not do induction over inductive predicates,
   every nontrivial consequence needs a `#@ lemma` (or Why3's `induction` transformation). Should
   PyCSL detect "this obligation needs the induction principle" and emit a targeted diagnostic
   pointing the author at a lemma stub?
2. **Triggers for predicate atoms.** How should e-matching instantiate quantified rules /
   consequences mentioning inductive-predicate atoms (ties to the quantifier-trigger proposal)?
3. **Reflection ergonomics.** Is there a sugar that, given a recursive boolean function *and* an
   inductive predicate, auto-generates the agreement-lemma obligation?
4. **Coinductive predicates.** Greatest-fixpoint definitions (safety, infinite/streaming JSON)
   are the dual; Why3 has support — worth a follow-on proposal, explicitly out of scope here.
5. **Cross-module reuse.** Sharing an inductive predicate (a reusable `wf_json` theory) across
   files points at the theory-cloning feature.

---

### Appendix — the three companion proposals as a unit

Inductive predicates complete a coherent trio for reasoning over `#@ datatype` structures:

- **Inductive predicates** *define* relations over the data (this proposal).
- **Typed quantifiers** let contracts *range over* the data and those relations.
- **Lemma functions** *prove* the inductive consequences the SMT solver cannot reach alone.

Each is a thin PyCSL surface over a capability Why3 already provides; together they move the
"needs an imported Rocq/Lean proof" boundary substantially outward.
