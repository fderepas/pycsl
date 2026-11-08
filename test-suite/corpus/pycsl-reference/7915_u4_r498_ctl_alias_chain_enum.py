r"""Test 7915 -- route #498 (control, expected PASS): `x = C.A; y = x; z = y; return z is x` -- one object through a chain of single plain assignments (an attribute read is no fresh value); CPython True
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


from enum import Enum


class C(Enum):
    A = 1
    B = 2


#@ no_exception \all
#@ ensures \result == True
def f(n: int) -> bool:
    x = C.A
    y = x
    z = y
    return z is x


if __name__ == "__main__":
    assert f(3) == True
