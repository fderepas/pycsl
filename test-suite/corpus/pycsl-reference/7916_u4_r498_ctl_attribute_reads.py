r"""Test 7916 -- route #498 (control, expected PASS): `C.A is C.A` -- an attribute read of enum members (an attribute read is no fresh value); CPython True
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
    return C.A is C.A


if __name__ == "__main__":
    assert f(3) == True
