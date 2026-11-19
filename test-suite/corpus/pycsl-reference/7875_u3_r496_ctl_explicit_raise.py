r"""Test 7875 -- route #496 (control, expected PASS): g holds an EXPLICIT `raise ValueError("neg")` (a builtin exception constructor, not an unlisted call) on a path its `requires n >= 0` excludes; f catches ValueError around g(n) and returns 0 there; `ensures \result == n + 1`; CPython f(3) returns 4
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


#@ requires n >= 0
#@ raises ValueError when n < 0
#@ ensures \result == n + 1
def g(n: int) -> int:
    if n < 0:
        raise ValueError("neg")
    return n + 1


#@ requires n >= 0
#@ ensures \result == n + 1
def f(n: int) -> int:
    try:
        return g(n)
    except ValueError:
        return 0


if __name__ == "__main__":
    assert f(3) == 4 and f(0) == 1
