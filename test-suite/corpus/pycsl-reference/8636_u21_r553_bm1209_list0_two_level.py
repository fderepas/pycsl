r"""Test 8636 -- route #553 (expected FAIL: PROVED at base int28, now NOT PROVED on a `PyCSL-R521` obligation; red team 52 probe g1312_bm1209_list0_two_level): the None store is in a SECOND callee `g2`, which g forwards the list to; CPython TypeError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ requires len(xs) >= 1
def g2(xs: List[int]) -> None:
    xs[0] = None


#@ requires len(xs) >= 1
def g(xs: List[int]) -> None:
    g2(xs)


#@ no_exception \all
def f(k: int, ys: List[int]) -> int:
    xs = [1]
    g(xs)
    return xs[0] + 1


if __name__ == "__main__":
    try:
        r = f(1, [1])
        print('result', r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
