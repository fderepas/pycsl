r"""Test 6664 -- route #441 B1 (expected FAIL): `n: int; int(n, 10)` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `k001_int_base_int.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(n: int) -> int:
    return int(n, 10)


if __name__ == "__main__":
    try:
        r = f(5)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
