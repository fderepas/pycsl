r"""Test 1946 — gen #36 (expected FAIL): W-IPM S-C NON-VACUITY twin of 1945.

Same `self.passes.extend(other.passes)` body, now lowered to
`self.passes <- Array.append self.passes other.passes`, under the claim that the length is
UNCHANGED — false whenever `other.passes` is non-empty (CPython grows the list). The
pre-S-C erasure (`val self_passes_extend_1 (x0: int) : int`, no `self`, no `writes`) is the
shape that WOULD have proved this; the faithful lowering must NOT.
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

    #@ ensures \length(self.passes) == \old(\length(self.passes))
    #@ assigns self.passes
    def extend(self, other: "Report") -> None:
        self.passes.extend(other.passes)
