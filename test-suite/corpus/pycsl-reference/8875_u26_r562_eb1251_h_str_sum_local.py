r"""Test 8875 -- route #562 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R562-COMPREHENSION-ELEMENT-KIND; red team 53 probe g1427/eb1251_h_str_sum_local.py): `g = (h(t) for x in xs); return sum(g)`; CPython TypeError: can only concatenate str (not "int") to str
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def h(x: int) -> int:
    return x + 1



#@ no_exception \all
def f(k: int, xs: List[int], t: str) -> int:
    g = (h(t) for x in xs)
    return sum(g)


if __name__ == "__main__":
    try:
        r = f(0, [1, 2], "ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
