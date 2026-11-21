r"""Test 7855 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): g's `next(x for x in xs)`; f catches StopIteration; CPython f([]) returns 2 (red team 44 probe g519/t51905_next_genexp_ens.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(xs: List[int]) -> int:
    y = next(x for x in xs)
    return 1


#@ ensures \result == 1
def f(xs: List[int]) -> int:
    try:
        return g(xs)
    except StopIteration:
        return 2


if __name__ == "__main__":
    try:
        r = f([])
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
