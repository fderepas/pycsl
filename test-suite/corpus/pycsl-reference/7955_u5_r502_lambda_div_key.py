r"""Test 7955 -- route #502 (expected FAIL: PROVED at base, REFUSED PYCSL-R502-CALLEE-COMPREHENSION-OBLIGATION): g's `sorted(xs, key=lambda v: 10 // v)`; f catches ZeroDivisionError; CPython returns 2 (red team 45 probe g600/a60022_lambda_div_key.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(xs: List[int]) -> int:
    ys = sorted(xs, key=lambda v: 10 // v)
    return 1


#@ ensures \result == 1
def f(xs: List[int]) -> int:
    try:
        return g(xs)
    except ZeroDivisionError:
        return 2


if __name__ == "__main__":
    try:
        r = f([0, 1])
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
