r"""Test 2062 — gen #36 (expected FAIL): NON-VACUITY twin of 2061 — after `self.d = {}` the
key "k" is ABSENT (CPython: `"k" in t.d` is False), so `\result == True` (the method answers `"k" in self.d`) must NOT prove.
"""
# pycsl-expected: FAIL
from typing import Dict


class Table:
    def __init__(self) -> None:
        self.d: Dict[str, str] = {}

    #@ ensures \result == True
    #@ assigns self.d
    def reset(self) -> bool:
        self.d = {}
        return "k" in self.d
