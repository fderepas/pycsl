r"""Test 8868 -- route #561 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R561-COMPREHENSION-NON-ITERABLE-OPERAND; red team 53 probe g1441/ep1216_rec_hay_listcomp.py): `return len([1 in p for x in xs])`; CPython TypeError: argument of type 'P' is not a container or iterable
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

@dataclass
class P:
    a: int



#@ no_exception \all
def f(k: int, xs: List[int], p: P, t: str) -> int:
    return len([1 in p for x in xs])


if __name__ == "__main__":
    try:
        r = f(1, [1, 2], P(1), "ab")
        print("result", repr(r)[:60])
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
