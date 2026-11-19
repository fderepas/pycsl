r"""Test 7858 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): a `\trusted` g holding `s.index("z")`; f catches ValueError; CPython f('a') returns 2 (red team 44 probe g514/c51401_sindex_trusted.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ \trusted reviewer: rt44
#@ ensures \result == 1
def g(s: str) -> int:
    y = s.index("z")
    return 1


#@ ensures \result == 1
def f(s: str) -> int:
    try:
        return g(s)
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
