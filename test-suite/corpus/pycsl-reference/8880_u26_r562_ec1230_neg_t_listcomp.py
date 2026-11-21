r"""Test 8880 -- route #562 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R562-COMPREHENSION-ELEMENT-KIND; red team 53 probe g1428/ec1230_neg_t_listcomp.py): `return len([-t for x in xs])`; CPython TypeError: bad operand type for unary -: 'str'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, xs: List[int], t: str, ws: List[str]) -> int:
    return len([-t for x in xs])


if __name__ == "__main__":
    try:
        r = f(0, [1, 2], "ab", ["a"])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
