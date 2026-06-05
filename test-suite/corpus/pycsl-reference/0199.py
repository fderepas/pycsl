"""Test 0199 — dict type support: reading values by key.

A `dict` parameter is modelled as a total `map int (option int)` (a missing key reads as 0), so
indexed reads `d[0]`, `d[1]` carry content and a postcondition over them discharges. (`\length`
on a dict is NOT supported — a total map has no cardinality; that boundary is documented by the
negative 0509.)"""
_ = 0  # anchor


#@ ensures \result == d[0] + d[1]
def sum_first_two(d: dict) -> int:
    """Sum the values at keys 0 and 1 of a dict-like mapping (missing key -> 0)."""
    return d[0] + d[1]
