**Introduction** and **inversion** are the two reasoning directions an
[inductive predicate](inductive-predicate.md) gives you "for free" — without an
explicit `#@ lemma`.

---

## Introduction (forward)

Prove a *concrete* instance of the predicate by applying its rules forward. For
`even` defined by `even(0)` and `even(m) ==> even(m + 2)`:

```python
#@ ensures even(4)        # even(0) → even(2) → even(4)
```

The SMT backend can chain the introduction rules to build a specific derivation,
so a ground goal like `even(4)` discharges directly (driver `0562`).

## Inversion (backward)

A value can *only* have been built by the rules, so you can rule cases out:

```python
#@ ensures not even(3)    # no rule produces 3
```

Why3 derives an inversion principle from the declaration: `even(n)` implies
`n = 0 \/ (n >= 2 /\ even(n - 2))`. The solver uses it to refute impossible
instances.

## The harder third direction

What is *not* free is a **universally-quantified consequence** over the whole
relation (`\forall n; even(n) ==> n >= 0`). That requires induction on the
derivation and a `#@ lemma` — see
[relational-consequence-via-lemma](relational-consequence-via-lemma.md). The
inversion principle is itself often packaged as an inversion lemma that the
consequence/reflection proofs cite (via [`#@ uses`](uses-ordering-citation.md)).
