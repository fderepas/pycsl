r"""Test 1965 — gen #36 (expected FAIL): NON-VACUITY twin of 1964 — the split path's list
is NOT empty in general, so the unconditional `len(\result) == 0` must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
from typing import List


#@ ensures len(\result) == 0
def names(line: str) -> List[str]:
    if not line:
        return []
    return [p.strip() for p in line.split(",")]
