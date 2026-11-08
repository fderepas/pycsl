r"""Test 1950 — gen #36 (expected PASS): W-IPM S-C3 — a `List[<record>]` self field declared in
a plain class's `__init__` (`self.warnings: List[Warn] = []`, the mirror
`ConcurrencyChecker.warnings` shape) is emitted as the faithful `array warn` (the element
record is pinned PURE by `list_element_record_types`), so the S-C arm lowers both
`self.warnings.append(Warn(...))` (a constructor of the element record) and
`self.warnings.append(w)` (a `Warn` parameter) to
`self.warnings <- Array.append self.warnings (Array.make 1 <rec>)`.
Before S-C3 the field was the element-erased `array int` and both appends were REFUSED (O7).
Twin: 1951 (false length claim, must FAIL).
"""
# pycsl-expected: PASS
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

    #@ ensures \length(self.warnings) == \old(\length(self.warnings)) + 1
    #@ assigns self.warnings
    def warn(self, var: str, line: int) -> None:
        self.warnings.append(Warn(kind="unprotected_shared", message=var, function="f", line=line))

    #@ ensures \length(self.warnings) == \old(\length(self.warnings)) + 1
    #@ assigns self.warnings
    def warn_rec(self, w: Warn) -> None:
        self.warnings.append(w)
