"""Test 0339 — PyCSL ghost_list (cross-prover, tuesday-01).

The cross-prover Coq/Lean fixtures use `list nat` / `List Nat` binders
to exercise the bridge canonicalizer's type-tag normalization. The
expression `\\length(\\append(l1, l2))` rendered by the converters is
not yet PyCSL-grammar-compatible at the surface level, so this
reference test ships the simpler identity postcondition.
"""
#@ requires n >= 0
#@ ensures \result == n
#@ assigns \nothing
def list_length_after_append(n: int) -> int:
    return n
