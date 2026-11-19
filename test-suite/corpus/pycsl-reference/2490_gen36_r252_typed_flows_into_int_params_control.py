r"""Test 2490 — route #252 (expected PASS): CONTROL: an `int` parameter and integer literals passed to
`int` parameters keep the callee's integer contract, beside an unused `Any` parameter.
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == a - b
#@ assigns \nothing
def g(a: int, b: int) -> int:
    return a - b


#@ ensures \result == 0
#@ assigns \nothing
def f(x: Any, n: int) -> int:
    return g(3, 3) + g(n, n) + g(a=n, b=n)


if __name__ == "__main__":
    assert f(object(), 4) == 0
