r"""Test 1948 — gen #36 (expected FAIL): W-IPM S-C element fidelity (review O7) — a
`List[Rec]` field whose record element is ERASED to `array int` (no `@mutable_state` /
IR-node gate, so the field is emitted `mutable out: array int`) is NOT lowered by the S-C
arm: the arm fires only when the field's recorded Python element type maps EXACTLY to the
emitted Why3 element type, and no record class maps to `int` (here Module 5 records no
element type for the field at all, which is refused the same way). Both the `append` and the
`extend` stay REFUSED, never `_coerce_to_int`'d into the array — which would make a
contents claim about the appended record unfalsifiable. (The `extend` is reported first.)
"""
# pycsl-expected: FAIL
from __future__ import annotations
_ = 0  # anchor
from dataclasses import dataclass, field
from typing import List


@dataclass
class Rec:
    k: int = 0


@dataclass
class Log:
    out: List[Rec] = field(default_factory=list)

    #@ ensures \length(self.out) == \old(\length(self.out)) + 1
    #@ assigns self.out
    def push(self, r: Rec) -> None:
        self.out.append(r)

    #@ ensures \length(self.out) == \old(\length(self.out)) + len(other.out)
    #@ assigns self.out
    def extend(self, other: "Log") -> None:
        self.out.extend(other.out)
