"""Test 0620 — quantification over a list element domain and an integer range (07-1311 Q1).

`\\forall x in a;` ranges over the elements of a list (membership desugar), and
`\\forall i in range(lo, hi);` over an integer interval — the latter now lowers to a direct
`lo <= i and i < hi` bound instead of mis-applying `Array.length` to a non-array (07-1311 Q1.2).
"""
# pycsl-flags: --memory-model hoare


#@ requires n >= 0 and m >= n
#@ ensures \forall i in range(n, m); i >= n
#@ assigns \nothing
def g(n: int, m: int) -> int:
    return 0


#@ requires \length(a) >= 0
#@ ensures \forall x in a; x == x
#@ assigns \nothing
def f(a: list) -> int:
    return 0
