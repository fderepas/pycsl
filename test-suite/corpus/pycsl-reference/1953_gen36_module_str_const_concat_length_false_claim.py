r"""Test 1953 — gen #36 (expected FAIL): NON-VACUITY twin of 1952 — the off-by-one claim
`len(PREFIX + s) == len(s) + 5` (`PREFIX` has 6 characters) must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
_ = 0  # anchor

PREFIX = "warn: "


#@ ensures \result == len(s) + 5
def tag_len(s: str) -> int:
    t = PREFIX + s
    return len(t)
