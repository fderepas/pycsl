**Inductive reflection** connects a logic-only [inductive
predicate](inductive-predicate.md) to an *executable* decision function, with an
**agreement lemma** proving the two coincide — so you can reason with the
predicate in specifications and compute with the function in code.

---

## The pieces

For `even`, reflection is built from a decision function and an agreement lemma:

```python
#@ requires n >= 0
#@ ensures \result == 0 or \result == 1
#@ \variant n
def even_dec(n: int) -> bool:
    return True if n == 0 else (False if n == 1 else even_dec(n - 2))

#@ lemma
#@ requires n >= 0
#@ ensures (even_dec(n) == 1) <==> even(n)
#@ \variant n
#@ uses even_inv
def even_agrees(n: int) -> None:
    if n == 0:
        pass
    elif n == 1:
        pass
    else:
        even_agrees(n - 2)
```

`even_dec` is a recursive `let function` (PyCSL models its `bool` result as `0`/`1`).
The agreement lemma is recursive — induction on `n` mirrors `even_dec`'s recursion,
so each recursive call supplies the induction hypothesis.

## What it composes

The agreement proof leans on the whole inductive toolkit:

- the **consequence** `even(n) ==> n >= 0`
  ([relational-consequence-via-lemma](relational-consequence-via-lemma.md)),
- the **inversion** lemma `even(n) ==> n == 0 or (n >= 2 and even(n - 2))`
  ([introduction & inversion](introduction-and-inversion.md), cited via
  [`#@ uses`](uses-ordering-citation.md)),
- and `even_dec`'s own recursion,

all discharged through Why3's `induction_pr` transformation.

## Two pitfalls (why the form matters)

- **Write `even_dec` as a single `return` of a conditional expression**, so it
  lowers to a clean unfoldable `if-then-else` logic function. A multi-`return` body
  lowers to `Return`-exception control flow, which is opaque to the agreement proof.
- A predicate application is **already a formula** — PyCSL must not `<> 0`-coerce
  `even(n - 2)` inside an `and`/`or` (the one emission fix reflection required).

Driver `0582`. See `test-suite/annotations.md` §2.8.
