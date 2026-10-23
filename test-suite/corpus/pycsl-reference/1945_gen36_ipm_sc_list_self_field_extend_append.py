r"""Test 1945 — gen #36 (expected PASS): W-IPM S-C — `self.<f>.extend(<recv>.<g>)` and
`self.<f>.append(v)` on a `List[str]` field of a `@dataclass` are real field write-backs.

Lowering: `self.passes <- Array.append self.passes other.passes` and
`self.passes <- Array.append self.passes (Array.make 1 s)` — a FRESH array of the summed
length, old elements preserved. The store puts `self.passes` in the function's effect, and
the declared `#@ assigns` governs the other fields through the emitted frame-preservation
`ensures { self.failures = old self.failures }`. At 645ce20d both calls were REFUSED
("MUTATES its receiver in place, and no certified lowering models it").
Twins: 1946 (false length claim, must FAIL), 1947 (caller), 1948 (O7: a record element
erased to `array int` stays REFUSED), 1949 (self-aliasing `r.extend(r)` fails closed).
"""
# pycsl-expected: PASS
from __future__ import annotations
_ = 0  # anchor
from dataclasses import dataclass, field
from typing import List


@dataclass
class Report:
    passes: List[str] = field(default_factory=list)
    failures: List[str] = field(default_factory=list)

    #@ ensures \length(self.passes) == \old(\length(self.passes)) + len(other.passes)
    #@ assigns self.passes
    def extend(self, other: "Report") -> None:
        self.passes.extend(other.passes)

    #@ ensures \length(self.passes) == \old(\length(self.passes)) + 1
    #@ assigns self.passes
    def add(self, s: str) -> None:
        self.passes.append(s)
