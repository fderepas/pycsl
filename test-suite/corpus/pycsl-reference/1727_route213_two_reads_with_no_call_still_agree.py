r"""Test 1727 — ROUTE #213 CONTROL: route #197's equality must survive the repair.

Two reads of the SAME `getattr` expression with NOTHING between them agree, and that is the
property route #197 deliberately bought when it made the device per-site rather than
`(any int)`. #213's refusal is keyed on the false-equality SHAPE — the same expression read
twice in a function that ALSO CALLS something — so this file must keep PROVING. If it ever
fails, the repair has become a ban on reading an attribute twice.

Route #255 (gen #36): expected PASS until route #255; expected FAIL (REFUSED) now. The claim is
FALSE in CPython: `o` is `Any`, so `getattr(o, "a")` may return an object whose `__sub__` returns 7,
and `x - y` is then 7. A `getattr` handed an erased value now returns an erased value (routes
#249/#251/#252), so the `int` arithmetic is refused; the per-site agreement of the two reads (route
#197) is not what changed.
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model hoare
from typing import Any

_ = 0  # anchor


#@ ensures \result == 0
def f(o: Any) -> int:
    x = getattr(o, "a")
    y = getattr(o, "a")
    return x - y
