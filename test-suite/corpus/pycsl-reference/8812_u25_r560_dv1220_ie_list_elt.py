r"""Test 8812 -- route #560 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R560-INTENUM-MEMBER-OPERAND; red team 53 probe g1421/dv1220_in_list_elt.py): `w = [IE.B]; return 1 if k in w[0] else 0`; CPython TypeError: argument of type 'IE' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

import enum


class IE(enum.IntEnum):
    A = 1
    B = 2



#@ no_exception \all
def f(k: int) -> int:
    w = [IE.B]
    return 1 if k in w[0] else 0


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
