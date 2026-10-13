r"""Test 1947 — gen #36 (expected PASS): W-IPM S-C caller — `n = len(r.passes); r.extend(o);
return n` emits and proves.

The local `n` holds an `int` read BEFORE the call, never the array, so Why3's reset rule
does not bite. The call goes through the method's abstract avatar
`val r_extend_1 (self: report) (x0: report) : unit writes { self.passes }`; its record
argument used to be default-typed `x0: int` (an L3-tc error) and is now the record (the
`_record_param_classes` type of `o`). The avatar havocs `r.passes`, so only claims about
the value read BEFORE the call are provable here.
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


#@ ensures \result == \old(len(r.passes))
#@ assigns r.passes
def count_then_extend(r: Report, o: Report) -> int:
    n = len(r.passes)
    r.extend(o)
    return n
