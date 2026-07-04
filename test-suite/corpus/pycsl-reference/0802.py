"""Test 0802 — NEGATIVE: in-place inner mutation a[i][j]=v is REJECTED, not
silently accepted as a false claim.

nested-list.md §5 boundary. The Gate-B representation is `array (seq τ)`: the
OUTER list is mutable (a whole-row reassignment `a[i] = row` is sound), but the
INNER `seq` is a PURE, immutable Why3 value — so an in-place inner update
`a[i][j] = v` has no sound WhyML rendering. Rather than emit an unsound update,
the transpiler REJECTS it (a hard verification failure: the inner `a[i]` is a
`seq int`, not an assignable `array int` cell). This test documents that
boundary — nested in-place mutation is out of scope for the read-only nested
model, never silently mis-modelled. (Ragged/read-only nested access IS faithful;
see 0797-0800.)
"""
# pycsl-expected: FAIL
_ = 0  # anchor
from typing import List

#@ requires 0 <= i and i < len(a)
#@ requires 0 <= j and j < len(a[i])
#@ ensures \result == 0
def bad_inner_mutate(a: List[List[int]], i: int, j: int, v: int) -> int:
    a[i][j] = v
    return 0
