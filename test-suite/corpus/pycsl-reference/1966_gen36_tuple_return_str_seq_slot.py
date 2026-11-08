r"""Test 1966 — gen #36 (expected PASS): a bare `-> tuple` function returning a Module5
SEQ-PROMOTED list local alongside an int (`return out, i`). The slot was typed `array int`
by `_refine_tuple_return_type` while the body returned the growable `seq`, so no such
function type-checked (L3-tc). The slot is now typed from the local's element type
(`array string` when every appended element is a string, the type `_mark_string_seq_locals`
infers) and the tail return bridges it with `materialize_str`/`materialize` (a fresh array
EQUAL to the seq). The loop-exit index is proved through the tuple. Twin: 1967 (must FAIL).
"""
# pycsl-expected: PASS
from __future__ import annotations
from typing import List


#@ requires 0 <= n and n <= len(raw)
#@ ensures \result[1] == n
def collect(raw: List[str], n: int) -> tuple:
    out: List[str] = []
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        out.append(raw[i].strip())
        i += 1
    return out, i


#@ requires 0 <= n
#@ ensures \result[1] == n
def count_up(n: int) -> tuple:
    out: List[int] = []
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        out.append(i)
        i += 1
    return out, i
