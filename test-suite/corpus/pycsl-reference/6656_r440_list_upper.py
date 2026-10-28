r"""Test 6656 -- route #440 A2 (expected FAIL): `xs: List[int]; xs.upper()` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `s104_xs_upper.py`); CPython raises AttributeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(n: int, s: str, x: float, xs: List[int], d: Dict[str, int], st: Set[int]) -> int:
    return len(xs.upper())


if __name__ == "__main__":
    try:
        r = f(1, "ab", 1.5, [1], {"a": 1}, {1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
