r"""Test 2131 — route #236 (expected PASS): CONTROL. The `None` actual SUPPLIED explicitly
(`P(c, None)`) was already the opaque `pycsl_none` and still is: `\result == 1` PROVES.
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
    p = P(c, None)
    if p.k is None:
        return 1
    return 2
