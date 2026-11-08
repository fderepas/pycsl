r"""Test 9252 -- route #577 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R577-ENUM-MEMBER-VALUE-OPERAND; red team 55 probe gk1730_mod_ee_in.py): `return 1 if k in MA.value else 0`; CPython TypeError argument of type 'int' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class IE(enum.IntEnum):
    A = 1
    B = 2


class EE(enum.Enum):
    A = 1
    B = 2

MA = EE.A


#@ no_exception \all
def f(k: int) -> int:
    return 1 if k in MA.value else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
