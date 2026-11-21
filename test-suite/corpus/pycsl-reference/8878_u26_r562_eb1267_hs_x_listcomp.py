r"""Test 8878 -- route #562 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R562-COMPREHENSION-ELEMENT-KIND; red team 53 probe g1427/eb1267_hs_x_listcomp.py): `return len([hs(x) for x in xs])`; CPython TypeError: unsupported operand type(s) for +: 'int' and 'str'
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def hs(x: str) -> int:
    return len(x + "c")



#@ no_exception \all
def f(k: int, xs: List[int], t: str) -> int:
    return len([hs(x) for x in xs])


if __name__ == "__main__":
    try:
        r = f(0, [1, 2], "ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
