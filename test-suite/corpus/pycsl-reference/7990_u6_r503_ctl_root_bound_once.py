r"""Test 7990 -- route #503 (control, expected PASS): `a = n + 1000; b = a; c = b` then an UNRELATED name rebound, `c is a` -- the root `a` is bound once, one object; CPython True
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


#@ ensures \result == True
def f(n: int) -> bool:
    a = n + 1000
    b = a
    c = b
    t = 3
    t = t + 1
    return c is a


if __name__ == "__main__":
    assert f(5) == True
