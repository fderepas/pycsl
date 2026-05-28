"""Test 0340 — PyCSL ghost_set (cross-prover, tuesday-01).

The Coq `nat -> bool` / Lean `Nat → Bool` characteristic-function
representation of sets passes through the bridge canonicalizer's
type-tag normalization to produce identical IR on both sides.
"""
#@ requires n >= 0
#@ ensures \forall s1; \forall s2; \result == n
#@ assigns \nothing
def set_union_eq(n: int) -> int:
    return n
