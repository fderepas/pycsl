r"""Test 2127 — route #236 (expected PASS): CONTROL for 2110. The omitted
`k: Optional[int] = None` IS `None`, and the opaque `pycsl_none` default makes `p.k is None`
decided True: `\result == 1` PROVES (refused at base, where `k` was `0`).
"""
# pycsl-expected: PASS
from dataclasses import dataclass
from typing import Optional


@dataclass
class P:
    x: int
    k: Optional[int] = None


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.k is None:
        return 1
    return 2
