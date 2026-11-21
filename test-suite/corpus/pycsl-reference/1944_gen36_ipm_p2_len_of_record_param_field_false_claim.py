r"""Test 1944 — gen #36 (expected FAIL): W-IPM prerequisite P2 — `len(<record-param>.<field>)`
over a `List[str]` field of a record PARAMETER is the array length, like `len(self.<field>)`.

At 397ada4f `len(other.passes)` lowered to `iter_length other.passes` — the opaque
`iter_length : int -> int` applied to an `array string`, a Why3 type error — because
`_handle_len_call` used `Array.length` only when the receiver was `self`. The `>= 0` conjunct
needs the real `Array.length` (an uninterpreted `iter_length` would not give it).
NON-VACUITY twin of 1943: the postcondition claims one MORE than the length; it must NOT prove.
"""
# pycsl-expected: FAIL
from __future__ import annotations
_ = 0  # anchor
from dataclasses import dataclass, field
from typing import List


@dataclass
class Report:
    passes: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)

    #@ ensures \result == len(other.passes) + len(self.failures) + 1
    #@ ensures \result >= 0
    #@ assigns \nothing
    def n(self, other: Report) -> int:
        return len(other.passes) + len(self.failures)
