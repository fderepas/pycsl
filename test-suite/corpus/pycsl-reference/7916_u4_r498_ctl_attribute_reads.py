r"""Test 7916 -- route #498 (control, expected PASS): `c.a is c.a` -- two reads of ONE stored field are one object (an attribute read is no fresh value); CPython True
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


class C:
    def __init__(self, n: int) -> None:
        self.a: int = n + 1000


#@ ensures \result == True
def f(c: C) -> bool:
    return c.a is c.a


if __name__ == "__main__":
    assert f(C(3)) == True
