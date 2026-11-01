r"""Test 7875 -- route #496 (control, expected PASS): g raises EXPLICITLY (`raise ValueError("neg")`: a builtin exception constructor, not an unlisted call); f catches it and returns 2; `ensures \result >= 1`; CPython f(-1) returns 2, f(3) returns 1
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


#@ raises ValueError when n < 0
#@ ensures \result == 1
def g(n: int) -> int:
    if n < 0:
        raise ValueError("neg")
    return 1


#@ ensures \result >= 1
def f(n: int) -> int:
    try:
        return g(n)
    except ValueError:
        return 2


if __name__ == "__main__":
    assert f(-1) == 2 and f(3) == 1
