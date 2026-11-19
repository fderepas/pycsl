r"""Test 1963 — gen #36 (expected FAIL): NON-VACUITY twin of 1962 — the loop stops at the
first BLANK line, so `\result == n` must NOT prove. (Had the string operand been dropped
from the condition, leaving `j < n`, this claim WOULD prove.)
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List


#@ requires 0 <= i and i <= n and n <= len(raw)
#@ ensures \result == n
def skip_nonblank(raw: List[str], i: int, n: int) -> int:
    j = i
    #@ loop invariant i <= j and j <= n
    #@ loop variant n - j
    while j < n and raw[j].strip():
        j += 1
    return j
