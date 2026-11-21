r"""Test 6672 -- route #441 B1 (expected FAIL): `d.get(1, 2, 3)` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `e033_get_three.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(d: Dict[int, int]) -> int:
    return d.get(1, 2, 3)


if __name__ == "__main__":
    try:
        r = f({})
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
