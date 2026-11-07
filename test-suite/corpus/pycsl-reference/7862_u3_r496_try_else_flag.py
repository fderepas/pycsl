r"""Test 7862 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL): g holding `t.index("z")`; f's `try: g(s) except ValueError: pass else: r = 1`; CPython f('a') returns 2 (red team 44 probe g524/h52402_try_else_flag.py)
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ ensures \result == 1
def g(t: str) -> int:
    y = t.index("z")
    return 1


#@ ensures \result == 1
def f(s: str) -> int:
    r = 2
    try:
        g(s)
    except ValueError:
        pass
    else:
        r = 1
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
