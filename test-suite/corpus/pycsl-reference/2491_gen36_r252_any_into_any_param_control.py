r"""Test 2491 — route #252 (expected PASS): CONTROL: an `Any` value passed to an `Any` parameter is not a
builtin slot; the callee's contract still applies.
"""
# pycsl-expected: PASS
from typing import Any


#@ ensures \result == 1
#@ assigns \nothing
def g(a: Any) -> int:
    return 1


#@ ensures \result == 2
#@ assigns \nothing
def f(x: Any) -> int:
    return g(x) + 1


if __name__ == "__main__":
    assert f(object()) == 2
