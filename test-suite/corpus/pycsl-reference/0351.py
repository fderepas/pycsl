"""Test 0351 — `sorted` builtin on a list parameter.

Exercises Module6's `sorted(arr)` emission: an abstract
`val sorted_1 (a: array int) : array int`. The abstract val has no
axioms about the result's contents — Why3 knows only that it returns
an array. The test contract therefore avoids claims about ordering
or element identity and only asserts a trivial property.

`s = sorted(values)` is recognised by Module6's assign-tracker
(via the `(sorted_1 ` prefix check), so `s` lands in `_array_locals`
and the body type-checks under full proof.

Purpose: lock in the emission shape so a future change that swaps
`sorted_1` for a different name (or drops it entirely) is caught by
the regression suite.
"""
#@ requires \length(values) >= 0
#@ ensures \result == 0
#@ assigns \nothing
def call_sorted(values: list) -> int:
    s = sorted(values)
    return 0

if __name__ == "__main__":
    assert call_sorted([3, 1, 2]) == 0
    assert call_sorted([]) == 0
    print("PASS")
