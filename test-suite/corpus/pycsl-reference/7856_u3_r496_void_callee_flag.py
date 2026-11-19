r"""Test 7856 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): an un-contracted void g holding `s.index("z")`; f's handler sets r = 2; CPython f('a') returns 2 (red team 44 probe g513/z51304_void_nocontract_flag.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

def g(s: str) -> None:
    y = s.index("z")


#@ ensures \result == 1
def f(s: str) -> int:
    r = 1
    try:
        g(s)
    except ValueError:
        r = 2
    return r


if __name__ == "__main__":
    try:
        r = f('a')
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
