r"""Test 2117 — route #236 (expected FAIL): a KEYWORD-ONLY
`field(default=None, kw_only=True)` omitted: route #146's by-name channel captures no default for
`None`, so the field fell to the definite `0` and `p.k == 0` PROVED; CPython `None`.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class P:
    x: int
    k: Optional[int] = field(default=None, kw_only=True)


#@ ensures \result == 1
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    if p.k == 0:
        return 1
    return 2
