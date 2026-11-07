r"""Test 6678 -- route #441 B1 (expected FAIL): `range(1, 2, 3, 4)` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `s009_range_1_2_3_4.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(n: int, s: str, x: float, xs: List[int], d: Dict[str, int], st: Set[int]) -> int:
    return len(range(1, 2, 3, 4))


if __name__ == "__main__":
    try:
        r = f(1, "ab", 1.5, [1], {"a": 1}, {1})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
