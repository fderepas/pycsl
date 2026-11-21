r"""Test 7857 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): `s.index("z")` three calls deep (g <- h <- h2); f catches ValueError; CPython f('a') returns 2 (red team 44 probe g513/z51316_depth3.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(s: str) -> int:
    y = s.index("z")
    return 1


#@ ensures \result == 1
def h(s: str) -> int:
    return g(s)


#@ ensures \result == 1
def h2(s: str) -> int:
    return h(s)


#@ ensures \result == 1
def f(s: str) -> int:
    try:
        return h2(s)
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
