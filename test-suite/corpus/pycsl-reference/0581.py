"""Test 0581 — universally-quantified consequence of an inductive predicate (inductive.md P3).

`even` is an inductive predicate. A consequence that holds of EVERY `even` value —
`\forall n; even(n) ==> n >= 0` — is NOT SMT-dischargeable directly (the solver would
have to invent the induction and times out). It is proved by INDUCTION on the derivation
of `even n`: PyCSL drives Why3's `induction_pr` transformation (after `split_vc`
introduces the `even n` premise) on files that declare an inductive predicate. The
`#@ lemma` states the consequence; its general fact is then usable by later goals
(inductive predicates + lemma functions are a pair).
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
