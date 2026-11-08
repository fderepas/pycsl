r"""Test 2063 — gen #36 (expected FAIL): the typed empty base of 2061 must not SWALLOW a later
store — after `self.d = {}; self.d["k"] = "v"` the key IS present (CPython: True), so
`\result == False` (the method answers `"k" in self.d`) must NOT prove.
"""
# pycsl-expected: FAIL
from typing import Dict


class Table:
    def __init__(self) -> None:
        self.d: Dict[str, str] = {}

    #@ ensures \result == False
    #@ assigns self.d
    def reset_and_put(self) -> bool:
        self.d = {}
        self.d["k"] = "v"
        return "k" in self.d
