r"""Test 7847 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): g's `y = s.index("z")`; f's `try: return g(s) except ValueError: return 2` under `ensures \result == 1`; CPython f('a') returns 2 (red team 44 probe g512/v51200_sindex_h.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

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
