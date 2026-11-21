r"""Test 1971 — gen #36 (expected FAIL): NON-VACUITY twin of 1970 — each call returns `n`
in its int slot, so `a + b == n + n + 1` must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List, Tuple


class Folder:
    #@ requires 0 <= n and n <= len(raw)
    #@ ensures \result[1] == n
    #@ assigns \nothing
    def collect(self, raw: List[str], n: int) -> Tuple[List[str], int]:
        out: List[str] = []
        i = 0
        #@ loop invariant 0 <= i and i <= n
        #@ loop variant n - i
        while i < n:
            out.append(raw[i].strip())
            i += 1
        return out, i

    #@ requires 0 <= n and n <= len(raw)
    #@ ensures \result == n + n + 1
    #@ assigns \nothing
    def twice(self, raw: List[str], n: int) -> int:
        first, a = self.collect(raw, n)
        second, b = self.collect(raw, n)
        return a + b
