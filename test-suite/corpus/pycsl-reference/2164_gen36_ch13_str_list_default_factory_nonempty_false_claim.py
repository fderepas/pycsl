r"""Test 2164 — ch13 seam S-a (expected FAIL): the omitted `List[str]` `default_factory=list`
field is EMPTY. CPython: `R().xs` is falsy, so `size_plus(k)` returns `k` and the claim `\result == k + 1` is false and must
stay unproved (the default is the length-0 `(Array.make 0 "")`, never a placeholder length).
Control: 2163.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import List


@dataclass
class R:
    xs: List[str] = field(default_factory=list)


#@ ensures \result == k + 1
#@ assigns \nothing
def size_plus(k: int) -> int:
    r = R()
    if r.xs:
        return k + 1
    return k
