"""WL-04d — FALSE TWIN: a filtered record projection is NOT length-preserving.

The faithful WL-04d law for `[p.x for p in a if p.x > 0]` gives only the length BOUND
`len(result) <= len(a)` and a membership existential — NEVER an exact length or a
per-index content law, because the result length is data-dependent (some records fail
the filter and are dropped). This driver falsely claims the filter keeps EVERY element
(`len(result) == len(a)`), which is false of real Python whenever any `p.x <= 0`. The
model must NOT prove it — the honest under-approximation is not vacuous/over-strong.

Verdict: UNPROVEN (the soundness oracle — PROVEN here would be UNSOUND).
"""
# pycsl-expected: FAIL
_ = 0
from dataclasses import dataclass
from typing import List


@dataclass
class Point:
    x: int
    y: int


#@ ensures \length(\result) == \length(a)
#@ assigns \nothing
def bogus_len(a: List[Point]) -> List[int]:
    return [p.x for p in a if p.x > 0]
