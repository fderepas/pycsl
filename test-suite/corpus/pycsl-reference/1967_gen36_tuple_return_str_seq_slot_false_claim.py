r"""Test 1967 — gen #36 (expected FAIL): NON-VACUITY twin of 1966 — the loop stops at `n`,
not one past it, so `\result[1] == n + 1` must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List


#@ requires 0 <= n and n <= len(raw)
#@ ensures \result[1] == n + 1
def collect(raw: List[str], n: int) -> tuple:
    out: List[str] = []
    i = 0
    #@ loop invariant 0 <= i and i <= n
    #@ loop variant n - i
    while i < n:
        out.append(raw[i].strip())
        i += 1
    return out, i
