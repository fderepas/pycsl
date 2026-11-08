r"""Test 2332 — route #246 (expected PASS until route #248; expected FAIL now): CONTROL. Route #239's `requires isinstance(x, T)` -> body
link is kept for a class whose `==` never crosses types: `requires isinstance(x, list)` decides the body
test, so `\result == 1` PROVES (CPython `f([1])` = 1).
Route #248: a contract-side `isinstance(<Any>, list)` was a function of the stored value, and the same value application let a caller's `requires y == z` discharge it for a non-list `z` (corpus 2353).
It is now REFUSED at the WhyML type-check (fail-closed); this true claim is the price of that refusal.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires isinstance(x, list)
#@ ensures \result == 1
#@ assigns \nothing
def f(x: Any) -> int:
    if isinstance(x, list):
        return 1
    return 0


if __name__ == "__main__":
    assert f([1]) == 1
