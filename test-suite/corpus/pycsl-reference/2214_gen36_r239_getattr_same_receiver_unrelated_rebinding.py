r"""Test 2214 — route #239 (expected PASS): CONTROL for 2206. Two reads of `getattr(o, "a", 0)`
with only an UNRELATED local rebound between them read the same state AND the same receiver,
so they are one term and `\result == 0` PROVES; CPython `f(C(1))` = 0.

Route #255 (gen #36): expected PASS until route #255; expected FAIL (REFUSED) now. The claim is
FALSE in CPython: `o` is `Any`, so `getattr(o, "a")` may return an object whose `__sub__` returns 7,
and `x - y` is then 7. A `getattr` handed an erased value now returns an erased value (routes
#249/#251/#252), so the `int` arithmetic is refused; the per-site agreement of the two reads (route
#197) is not what changed.
"""
# pycsl-expected: FAIL
from typing import Any


#@ ensures \result == 0
def f(o: Any) -> int:
    x = getattr(o, "a", 0)
    q = 1
    q = 2
    y = getattr(o, "a", 0)
    return x - y + q - 2
