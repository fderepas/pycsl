r"""Test 8882 -- route #562 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R562-COMPREHENSION-ELEMENT-KIND; red team 53 probe g1428/ec1236_x_in_t_listcomp.py): `return len([x in t for x in xs])`; CPython TypeError: 'in <string>' requires string as left operand, not int
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(k: int, xs: List[int], t: str, ws: List[str]) -> int:
    return len([x in t for x in xs])


if __name__ == "__main__":
    try:
        r = f(0, [1, 2], "ab", ["a"])
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
