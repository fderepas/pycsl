r"""Test 8871 -- route #561 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R561-COMPREHENSION-NON-ITERABLE-OPERAND; red team 53 probe g1441/ep1220_rec_nested_listcomp.py): `return len([[y for y in p] for x in xs])`; CPython TypeError: 'P' object is not iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int



#@ no_exception \all
def f(k: int, xs: List[int], p: P, t: str) -> int:
    return len([[y for y in p] for x in xs])


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], P(1), "ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
