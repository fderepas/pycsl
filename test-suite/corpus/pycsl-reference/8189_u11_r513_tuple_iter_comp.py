r"""Test 8189 -- route #513 (expected FAIL: PROVED at base `no_exception \all`, REFUSED PYCSL-R508-INT-FLOAT-PROMOTION-UNMODELLED; red team 47 probe g809/l8029_tupIF_iter_comp): `[a * 0.5 for a in t]` over `Tuple[int, float]`: every element read at the last argument's kind; CPython f((10**400, 0.5)) raises OverflowError
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union, Iterator, Sequence, FrozenSet
from dataclasses import dataclass

#@ no_exception \all
def f(t: Tuple[int, float]) -> int:
    v = [a * 0.5 for a in t]
    return 1


if __name__ == "__main__":
    try:
        r = f((10**400, 0.5))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
