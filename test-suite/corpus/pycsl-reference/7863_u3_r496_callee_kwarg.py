r"""Test 7863 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): g holding `t.index("z", k)`, called with a keyword; f catches ValueError; CPython f('a') returns 2 (red team 44 probe g522/p52206_callee_kwarg.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(t: str, k: int = 0) -> int:
    y = t.index("z", k)
    return 1


#@ ensures \result == 1
def f(s: str) -> int:
    try:
        return g(s, k=0)
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f('a')
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
