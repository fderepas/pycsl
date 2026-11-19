r"""Test 8809 -- route #560 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R560-INTENUM-MEMBER-OPERAND; red team 53 probe g1419/dt1212_ie_param_genexp_sum.py): `def f(k: int, e: IE): return sum(1 for x in e)`; CPython TypeError: 'IE' object is not iterable
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
def f(k: int, e: IE) -> int:
    return sum(1 for x in e)


if __name__ == "__main__":
    try:
        r = f(1, IE.A)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
