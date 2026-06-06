"""Test 0570 — recursive lemma WITHOUT `#@ \variant` proves (remains-2.md decision A).

`nat_to_int_nonneg` recurses structurally on `Nat` with NO `#@ \variant` clause. PyCSL
no longer rejects this (the variant-on-recursion check was dropped — it added no
soundness and was over-restrictive): **Why3 infers the structural variant** and the
induction discharges `to_int(n) >= 0`. Contrast 0559 (same proof, with an explicit
`#@ \variant n` — also fine) and 0560 (ill-founded recursion → rejected by Why3).
"""
# pycsl-flags: --memory-model hoare
_ = 0  # anchor


#@ datatype Nat = Z | S(Nat)


#@ \variant n
#@ assigns \nothing
def to_int(n: Nat) -> int:
    match n:
        case Z():
            return 0
        case S(m):
            return 1 + to_int(m)


#@ lemma
#@ ensures to_int(n) >= 0
#@ assigns \nothing
def nat_to_int_nonneg(n: Nat) -> None:
    match n:
        case Z():
            pass
        case S(m):
            nat_to_int_nonneg(m)
