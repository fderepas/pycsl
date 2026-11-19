r"""Test 8542 -- route #540 (expected FAIL: PROVED at base, REFUSED PYCSL-R545-NONE-OPERAND; red team 51 probe cc1214_pos_pos_n): `w = +r.n` of an `Optional[int]` @dataclass field holding None (route #527 bypass); CPython f(R(None, "ab", None, None)) raises TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class R:
    s: Optional[str]
    t: str
    n: Optional[int]
    x: Optional[float]


#@ no_exception \all
def f(r: R) -> int:
    w = +r.n
    return 1


if __name__ == "__main__":
    try:
        r = f(R(None, "ab", None, None))
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
