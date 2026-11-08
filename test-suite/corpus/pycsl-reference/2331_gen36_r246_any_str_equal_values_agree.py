r"""Test 2331 — route #246 (expected PASS until route #248; expected FAIL now): CONTROL. `str`'s builtin `==` never holds across types,
so a contract-side `isinstance(<Any>, str)` keeps route #239's value application and `requires x == y`
still PROVES the two tests agree (CPython: `"a" == "a"` both str; `"a" == 1` is False).
Route #248: `PyVal`/`Any` admit any object, so this relied on BUILTIN `==`; CPython `x = W()` with a user `__eq__` (always True), `y = "s"` makes the claim FALSE (corpus 2350). The contract-side
test is now REFUSED at the WhyML type-check (fail-closed); it was a FALSE claim, not a control.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires x == y
#@ ensures isinstance(x, str) == isinstance(y, str)
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


if __name__ == "__main__":
    assert isinstance("a", str) == isinstance("a", str)
    assert ("a" == 1) is False
