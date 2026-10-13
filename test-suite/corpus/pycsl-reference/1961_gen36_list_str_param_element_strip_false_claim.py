r"""Test 1961 — gen #36 (expected FAIL): NON-VACUITY twin of 1960 — stripping may SHORTEN
the element, so `len(raw[i].strip()) == len(raw[i])` must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List


#@ requires 0 <= i and i < len(raw)
#@ ensures \result == len(raw[i])
def stripped_len(raw: List[str], i: int) -> int:
    return len(raw[i].strip())
