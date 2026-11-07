r"""Test 8547 -- route #545 (expected FAIL: PROVED at base, REFUSED PYCSL-R545-NONE-OPERAND; red team 51 probe ww1211_neg_none): `w = -None`; CPython f(1) raises TypeError (bad operand type for unary -)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int) -> int:
    w = -None
    return 1


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
