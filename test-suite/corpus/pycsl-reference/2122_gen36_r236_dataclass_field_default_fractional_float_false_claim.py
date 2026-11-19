r"""Test 2122 — route #236 (expected FAIL): the `field(default=2.5)` spelling of
2121: truncated to 2, `\result == 2` PROVED; CPython 2.5.
"""
# pycsl-expected: FAIL
from dataclasses import dataclass, field


@dataclass
class P:
    x: int
    k: int = field(default=2.5)


#@ ensures \result == 2
#@ assigns \nothing
def g(c: int) -> int:
    p = P(c)
    return p.k
