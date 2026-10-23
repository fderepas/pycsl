r"""Test 1860 — ROUTE #213, the THREE-ARGUMENT spelling of the same defect.

Identical to 1859 except that both reads write a default: `getattr(o, "a", 0)`. An
UNKNOWN receiver takes the per-site constant WHETHER OR NOT a default is written, so the
three-argument form proved the same `\result == 0` over `x - y`.

It is here because gen #30's refusal MISSED THIS SPELLING — it was keyed on
`len(args) <= 2` because the first witness used the no-default form — and that was the
second time in one day a guard was derived from the shape of the witness instead of from
the property (route #208 was the first, twenty minutes after #206). The state-keyed
device closes both arms at once because it is keyed on the property: the device reads the
object state, and the object state moved.
"""
# pycsl-expected: FAIL
from typing import Any

_ = 0  # anchor


#@ assigns o.a
def mutate(o: Any) -> None:
    o.a = 99


#@ assigns o.a
#@ ensures \result == 0
def f(o: Any) -> int:
    x = getattr(o, "a", 0)
    mutate(o)
    y = getattr(o, "a", 0)
    return x - y
