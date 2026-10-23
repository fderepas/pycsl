r"""Test 1727 — ROUTE #213 CONTROL: route #197's equality must survive the repair.

Two reads of the SAME `getattr` expression with NOTHING between them agree, and that is the
property route #197 deliberately bought when it made the device per-site rather than
`(any int)`. #213's refusal is keyed on the false-equality SHAPE — the same expression read
twice in a function that ALSO CALLS something — so this file must keep PROVING. If it ever
fails, the repair has become a ban on reading an attribute twice.
"""
# pycsl-expected: PASS
# pycsl-flags: --memory-model hoare
from typing import Any

_ = 0  # anchor


#@ ensures \result == 0
def f(o: Any) -> int:
    x = getattr(o, "a")
    y = getattr(o, "a")
    return x - y
