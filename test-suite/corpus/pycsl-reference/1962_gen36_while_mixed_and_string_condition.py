r"""Test 1962 — gen #36 (expected PASS): a `while` condition `j < n and raw[j].strip()` mixes
an int-valued comparison with a STRING operand. Its value form (`and` selects an operand)
has no Why3 type, so it never type-checked; as a CONDITION only truthiness is observed and
Python's `bool(a and s)` is `bool(a) && len(s) != 0`, short-circuit included. Emitted:
`while ((!j < n) && (str_length_op ((str_strip_op raw[!j])) <> 0))`. Twin: 1963.
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List


#@ requires 0 <= i and i <= n and n <= len(raw)
#@ ensures i <= \result and \result <= n
def skip_nonblank(raw: List[str], i: int, n: int) -> int:
    j = i
    #@ loop invariant i <= j and j <= n
    #@ loop variant n - j
    while j < n and raw[j].strip():
        j += 1
    return j
