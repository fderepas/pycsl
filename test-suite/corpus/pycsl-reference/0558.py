"""Test 0558 — non-recursive lemma function (lemma.md P1).

A `#@ lemma` is a PROVED logical fact: Why3 verifies the (here empty) body against
the contract, then `forall a b. a>=0 and b>=0 -> a+b>=0` is available to later
goals. Lowers to `let lemma sum_nonneg (a b: int) : unit requires {…} ensures {…}
= ()`. SMT discharges the body directly — no induction, no `\variant`.

Contrast: `#@ \trusted` (assumed), `#@ proof` (proved elsewhere, an axiom). A
`#@ lemma` introduces NO axiom that isn't itself checked.
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ lemma
#@ requires a >= 0 and b >= 0
#@ ensures a + b >= 0
#@ assigns \nothing
def sum_nonneg(a: int, b: int) -> None:
    pass
