r"""Test 9254 -- route #577 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R577-ENUM-MEMBER-VALUE-OPERAND; red team 55 probe gy1608_ee_field_sumgen.py): `return sum(1 for x in q.e.value)`; CPython TypeError 'int' object is not iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class EE(enum.Enum):
    A = 1
    S = "ab"


class FL(enum.IntFlag):
    R = 1


@dataclass
class Q:
    e: EE


#@ no_exception \all
def f(k: int, q: Q) -> int:
    return sum(1 for x in q.e.value)


if __name__ == "__main__":
    try:
        print("result", repr(f(1, Q(EE.A)))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
