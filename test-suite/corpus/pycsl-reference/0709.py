"""Test 0709 — `\length(array_local)` in a loop invariant (emission regression).

A mutable array LOCAL (`out = [0]*n`) is bound as a plain `Array.make` mutable array, NOT
a ref, so it must be referenced BARE everywhere. The `\length` spec handler used to deref
it as `Array.length !out` inside a loop invariant (because the local also appears in
`local_refs`), a deref of a non-ref → WhyML typecheck failure. `len(out)` and the subscript
`out[i]` were already correct (both route through `_handle_var_expr`'s `_array_locals` rule
that returns array locals bare); only the `\length` path diverged. The fix excludes
`_array_locals` from the `\length` deref, mirroring the var rule.

This test pins the fix: `\length(out)` in a loop invariant alongside a subscript invariant
typechecks (emits `Array.length out`) and the function proves.
"""

from typing import List


#@ ensures \length(\result) == 8
#@ ensures \forall i: int; (0 <= i and i < 8) ==> \result[i] == 0
def zeros8() -> list:
    out = [0] * 8
    #@ loop invariant 0 <= i and i <= 8
    #@ loop invariant \length(out) == 8
    #@ loop invariant \forall j: int; (0 <= j and j < i) ==> out[j] == 0
    #@ loop variant 8 - i
    for i in range(8):
        out[i] = 0
    return out
