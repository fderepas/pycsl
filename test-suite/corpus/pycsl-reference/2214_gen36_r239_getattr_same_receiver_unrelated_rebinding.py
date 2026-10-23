r"""Test 2214 — route #239 (expected PASS): CONTROL for 2206. Two reads of `getattr(o, "a", 0)`
with only an UNRELATED local rebound between them read the same state AND the same receiver,
so they are one term and `\result == 0` PROVES; CPython `f(C(1))` = 0.
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == 0
def f(o: Any) -> int:
    x = getattr(o, "a", 0)
    q = 1
    q = 2
    y = getattr(o, "a", 0)
    return x - y + q - 2
