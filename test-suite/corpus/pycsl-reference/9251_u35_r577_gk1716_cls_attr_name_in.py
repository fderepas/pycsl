r"""Test 9251 -- route #577 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R571-ENUM-MEMBER-NAME-KIND; red team 55 probe gk1716_cls_attr_name_in.py): `return 1 if k in H.m.name else 0`; CPython TypeError 'in <string>' requires string as left operand, not int
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

class H:
    m = IE.A


#@ no_exception \all
def f(k: int) -> int:
    return 1 if k in H.m.name else 0


if __name__ == "__main__":
    try:
        print("result", repr(f(1))[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
