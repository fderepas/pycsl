r"""Test 9255 -- route #577 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R577-ENUM-MEMBER-VALUE-OPERAND; red team 55 probe gy1612_ee_local_alias_in.py): `m = EE.A`; `return 1 if k in m.value else 0`; CPython TypeError argument of type 'int' is not a container or iterable
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
def f(k: int, e: EE, q: Q) -> int:
    m = EE.A
    return 1 if k in m.value else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1, EE.A, Q(EE.A)))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
