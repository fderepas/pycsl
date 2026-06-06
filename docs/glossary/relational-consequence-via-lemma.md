**Relational-consequence-via-lemma** is the technique for proving a
universally-quantified property that holds of *every* element an inductive
predicate accepts — by stating it as a `#@ lemma` and discharging it through the
predicate's induction principle, rather than trying to get an SMT solver to find
it directly.

---

## The setup

An inductive predicate defines a relation by its introduction rules. For example:

```python
#@ inductive even(n: int):
#@     even_zero: even(0)
#@     even_step: \forall m: int; even(m) ==> even(m + 2)
```

This says exactly which numbers are even — built up from the base case `even(0)`
and the step rule.

## The problem

Suppose you want to prove a *consequence* — a fact true of all things in the
relation:

```python
\forall n: int; even(n) ==> n >= 0
```

An SMT solver generally cannot prove this on its own. The predicate `even` is
opaque to it; there is no finite case-split that establishes the property for the
(unbounded) set of even numbers. You need to reason by induction on the
*derivation* of `even(n)` — i.e., the induction principle Why3 derives from the
inductive declaration.

## "via-lemma"

The mechanism is: write the consequence as a `#@ lemma`, and prove it using the
inductive's induction/inversion principles. Why3 generates, for each inductive
predicate, an induction scheme (and inversion lemmas). The lemma's proof
case-splits on how `even(n)` could have been derived:

- **`even_zero` case:** `n = 0`, so `n >= 0` ✓
- **`even_step` case:** `n = m + 2` with `even(m)`; by the induction hypothesis
  `m >= 0`, so `n = m + 2 >= 0` ✓

Once the lemma is verified, its general fact `\forall n. even(n) -> n >= 0`
becomes available to later goals — so other functions can rely on the consequence
without re-proving it.

## Why "relational"

The term emphasizes that the inductive predicate is a *relation* (a least
fixpoint), and the technique extracts a logical consequence of membership in that
relation. It contrasts with what an inductive predicate gives you "for free":
**introduction** (proving a specific instance like `even(4)` by applying rules
forward) and **inversion** (e.g. `not even(3)`). A universally-quantified
consequence over the whole relation is the harder direction and is the thing that
needs the lemma + induction principle — hence *relational-consequence-via-lemma*.
In the project's framing, inductive predicates and `#@ lemma` functions are
described as **"a pair"** precisely because this is how you get
universally-quantified consequences out of an inductive definition.

## How PyCSL discharges it

PyCSL drives Why3's **`induction_pr`** proof transformation: for any module that
declares an inductive predicate, `pycsl.py::_run_proofs` appends `-a induction_pr`
to the Why3 command (after `split_vc` has introduced the `even n` premise into the
hypotheses, where `induction_pr` can act on it). It is a no-op on goals with no
inductive-predicate hypothesis, so non-inductive files are unaffected.

This is the load-bearing step that lets the [reference test](reference-test.md)
`0581` discharge `\forall n; even(n) ==> n >= 0`. It also underpins the heavier
inductive proofs that build on it: the **inversion lemma**
(`even(n) ==> n == 0 or (n >= 2 and even(n - 2))`) and, on top of that,
**reflection** — connecting `even` to an executable decision function `even_dec`
with an agreement lemma `even_dec(n) == 1 <==> even(n)` (driver `0582`).

See `test-suite/annotations.md` §2.8 and the
[static-semantics reference](../pycsl-static-semantics-reference.md) §2.8.
