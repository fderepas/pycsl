r"""Test 2326 — route #246 (expected FAIL): a callee PRECONDITION discharged by an `==` value of
another type. `g` requires `isinstance(x, int)` (`subtag (typeof_op x) tag_int`); the caller knows it of
`a` and `a == b`, so the call `g(b)` was PROVED safe at f777e2bd. CPython `m(1, 1.0)` calls `g(1.0)`,
violating `g`'s precondition. A contract-side `isinstance(<Any>, int)` is refused now.
"""
# pycsl-expected: FAIL
from typing import Any


#@ requires isinstance(x, int)
#@ ensures \result == 1
#@ assigns \nothing
def g(x: Any) -> int:
    return 1


#@ requires isinstance(a, int)
#@ requires a == b
#@ ensures \result == 1
#@ assigns \nothing
def m(a: Any, b: Any) -> int:
    return g(b)


if __name__ == "__main__":
    assert 1 == 1.0
    assert not isinstance(1.0, int)
