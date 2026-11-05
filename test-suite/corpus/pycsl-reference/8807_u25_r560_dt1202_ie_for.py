r"""Test 8807 -- route #560 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R560-INTENUM-MEMBER-OPERAND; red team 53 probe g1419/dt1202_ie_b_for.py): `for x in IE.B: c += 1`; CPython TypeError: 'IE' object is not iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class IE(enum.IntEnum):
    A = 1
    B = 2


class FL(enum.IntFlag):
    R = 1
    W = 2



#@ no_exception \all
def f(k: int) -> int:
    c = 0
    for x in IE.B:
        c += 1
    return c


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
