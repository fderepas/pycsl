r"""Test 7861 -- route #496 (expected FAIL: PROVED at base, REFUSED PYCSL-R496-CALLEE-UNLISTED-CALL (store model)): a `\trusted` g holding `math.sqrt(n)`, store model; f catches ValueError; CPython f(-1) returns 2 (red team 44 probe g514/c51407_sqrt_trusted.py)
"""
# pycsl-expected: FAIL
# pycsl-flags: --memory-model store
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ \trusted reviewer: rt44
#@ ensures \result == 1
def g(n: int) -> int:
    import math
    y = math.sqrt(n)
    return 1


#@ ensures \result == 1
def f(n: int) -> int:
    try:
        return g(n)
    except ValueError:
        return 2


if __name__ == "__main__":
    try:
        r = f(-1)
        if r != 1:
            print("VIOLATION contract", r)
        else:
            print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
