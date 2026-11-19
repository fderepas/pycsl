r"""Test 9249 -- route #577 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R560-INTENUM-MEMBER-OPERAND; red team 55 probe gk1682_mod_call_sumgen.py): `return sum(1 for x in MA.value)`; CPython TypeError 'int' object is not iterable
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

MA = IE(1)


#@ no_exception \all
def f(k: int) -> int:
    return sum(1 for x in MA.value)


if __name__ == "__main__":
    try:
        print("result", repr(f(1))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
