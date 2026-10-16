r"""Test 2331 — route #246 (expected PASS): CONTROL. `str`'s builtin `==` never holds across types,
so a contract-side `isinstance(<Any>, str)` keeps route #239's value application and `requires x == y`
still PROVES the two tests agree (CPython: `"a" == "a"` both str; `"a" == 1` is False).
"""
# pycsl-expected: PASS
from typing import Any


#@ requires x == y
#@ ensures isinstance(x, str) == isinstance(y, str)
#@ assigns \nothing
def f(x: Any, y: Any) -> int:
    return 0


if __name__ == "__main__":
    assert isinstance("a", str) == isinstance("a", str)
    assert ("a" == 1) is False
