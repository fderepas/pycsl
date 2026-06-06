A **lemma function** (`#@ lemma`) is a Python function whose body is a *proof*: a
PROVED logical fact, checked by Why3, whose conclusion becomes available to later
goals. It is the partner of the [inductive predicate](inductive-predicate.md) —
the two are "a pair," because lemmas are how you extract
universally-quantified consequences from an inductive definition.

---

## Shape

```python
#@ lemma
#@ ensures \forall n: int; even(n) ==> n >= 0
def even_nonneg() -> None:
    pass
```

It lowers to a Why3 `let [rec] lemma name (params) : unit requires {H} ensures {C}
= <proof body>`: Why3 verifies the body, then the general fact `forall params. H
-> C` is usable globally — so other functions rely on it without re-proving.

- **Non-recursive** lemmas are discharged by SMT directly.
- **Recursive** lemmas are proofs by induction: the self-call is the induction
  hypothesis (driver `0559`; the reflection agreement lemma `even_agrees`).

## Well-formedness (Module 4 enforces)

A lemma is **ghost**: return type `None`, `assigns \nothing`, and no `return
<value>` in the body. It states ≥1 `#@ ensures`, is not `#@ \diverges`, and may
**not** call a `\trusted` function — that would smuggle an unverified fact into a
"proved" lemma (Why3 cannot catch this; PyCSL rejects it).

## Termination is the backend's job

`#@ \variant` on a recursive lemma is **optional**: Why3 infers a structural
variant and rejects ill-founded recursion via its termination VC, so a
non-terminating "lemma" cannot export `False`
([backend-as-enforcer](backend-as-enforcer.md)). Supply `#@ \variant` only for a
*non-structural* measure (e.g. a lemma recursing on `n - 2`).

## Versus `#@ proof`

A `#@ proof rocq|lean` cites a theorem proved *elsewhere* (an audited axiom); a
`#@ lemma` is proved *here* and introduces no axiom that is not itself checked.

Drivers `0558` (SMT), `0559`/`0570` (recursive/inductive). See
`test-suite/annotations.md` §2.1.16.
