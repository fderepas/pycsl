r"""Test 7851 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): g's `divmod` by a parameter; f catches ZeroDivisionError; CPython returns 2 (red team 44 probe g512/v51240_divmod_zero_h.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(n: int) -> int:
    q, r = divmod(5, n)
    return 1


#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except ZeroDivisionError:
        return 2


if __name__ == "__main__":
    try:
        r = f(0)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
