r"""Test 8810 -- route #560 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R560-INTENUM-MEMBER-OPERAND; red team 53 probe g1419/dt1214_ie_local_in.py): `w = IE.A; return 1 if k in w else 0`; CPython TypeError: argument of type 'IE' is not a container or iterable
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
    w = IE.A
    return 1 if k in w else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
