r"""Test 1949 — gen #36 (expected FAIL): W-IPM S-C self-aliasing (review O4) — `r.extend(r)`
fails CLOSED.

The callee is the 1945 shape (`self.passes <- Array.append self.passes other.passes`). At
the call `r.extend(r)` the avatar `r_extend_1 r r` both WRITES `r.passes` and READS it
through the second argument; Why3 rejects it ("This application creates an illegal
alias"), so nothing is proved — CPython doubles the list, and the (false) claim below that
the length is unchanged must never be certified.
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

    #@ ensures \length(self.passes) == \old(\length(self.passes)) + len(other.passes)
    #@ assigns self.passes
    def extend(self, other: "Report") -> None:
        self.passes.extend(other.passes)


#@ ensures \result == len(r.passes)
#@ assigns r.passes
def double(r: Report) -> int:
    n = len(r.passes)
    r.extend(r)
    return n
