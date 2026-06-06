"""Test 0582 — inductive reflection: decision function + agreement lemma (inductive.md P4).

The logic-only inductive predicate `even` is connected to an EXECUTABLE/computational
decision function `even_dec` (a recursive `let function` returning 1/0) by an AGREEMENT
lemma `even_dec(n) == 1 <==> even(n)`, proved by induction. This is reflection: it lets
one reason with the predicate `even` in specs while computing with `even_dec`.

The proof composes the inductive toolkit:
  - `even_nonneg`  — the consequence `even(n) ==> n >= 0` (induction on the derivation).
  - `even_inv`     — the inversion `even(n) ==> n == 0 or (n >= 2 and even(n - 2))`
                     (induction on the derivation; needs `even_nonneg`, cited via `#@ uses`).
  - `even_dec`     — the recursive decision function.
  - `even_agrees`  — the agreement, a recursive lemma (induction on `n`) using `even_inv`.

All discharge via `split_vc` + `induction_pr` (PyCSL adds the latter for inductive modules).
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ inductive even(n: int):
#@     even_zero: even(0)
#@     even_step: \forall m: int; even(m) ==> even(m + 2)


#@ lemma
#@ ensures \forall n: int; even(n) ==> n >= 0
#@ assigns \nothing
def even_nonneg() -> None:
    pass


#@ lemma
#@ ensures \forall n: int; even(n) ==> (n == 0 or (n >= 2 and even(n - 2)))
#@ uses even_nonneg
#@ assigns \nothing
def even_inv() -> None:
    pass


#@ requires n >= 0
#@ ensures \result == 0 or \result == 1
#@ \variant n
#@ assigns \nothing
def even_dec(n: int) -> bool:
    # single-return conditional expression → a clean unfoldable `if-then-else` logic
    # function (no `Return`-exception control flow), so the agreement lemma can reason
    # through `even_dec`'s definition.
    return True if n == 0 else (False if n == 1 else even_dec(n - 2))


#@ lemma
#@ requires n >= 0
#@ ensures (even_dec(n) == 1) <==> even(n)
#@ \variant n
#@ uses even_inv
#@ assigns \nothing
def even_agrees(n: int) -> None:
    if n == 0:
        pass
    elif n == 1:
        pass
    else:
        even_agrees(n - 2)
