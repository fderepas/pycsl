r"""Test 7932 -- route #499 (control, expected PASS): `exec("t = 2")` in a function binds a name the function never mentions -- CPython's snapshot binding is unobservable, so the splice is harmless (rt44 control g517/e51704); CPython n
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


#@ ensures \result == n
def f(n: int) -> int:
    exec("t = 2")
    return n


if __name__ == "__main__":
    assert f(4) == 4
