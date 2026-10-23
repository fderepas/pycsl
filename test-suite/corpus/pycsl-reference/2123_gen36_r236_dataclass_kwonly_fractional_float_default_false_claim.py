r"""Test 2123 — route #236 (expected FAIL): a keyword-only
`field(default=2.5, kw_only=True)`: `_dc_default_const` truncated it to 2 and `\result == 2` PROVED;
CPython 2.5.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field


@dataclass
class P:
    x: int
    k: int = field(default=2.5, kw_only=True)


#@ ensures \result == 2
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    return p.k
