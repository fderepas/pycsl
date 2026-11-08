r"""Test 1951 — gen #36 (expected FAIL): W-IPM S-C3 NON-VACUITY twin of 1950 — same
record appends, under the FALSE claim that the length of `self.warnings` is unchanged
(CPython grows the list by one). The faithful `Array.append` lowering must NOT prove it.
"""
# pycsl-expected: FAIL
from __future__ import annotations
_ = 0  # anchor
from dataclasses import dataclass
from typing import List


@dataclass
class Warn:
    kind: str
    message: str
    function: str = ""
    line: int = 0


class Checker:
    def __init__(self, n: int) -> None:
        self.n = n
        self.warnings: List[Warn] = []

    #@ ensures \length(self.warnings) == \old(\length(self.warnings))
    #@ assigns self.warnings
    def warn(self, var: str, line: int) -> None:
        self.warnings.append(Warn(kind="unprotected_shared", message=var, function="f", line=line))

    #@ ensures \length(self.warnings) == \old(\length(self.warnings))
    #@ assigns self.warnings
    def warn_rec(self, w: Warn) -> None:
        self.warnings.append(w)
