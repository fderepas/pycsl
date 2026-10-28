r"""Test 6674 -- route #441 B1 (expected FAIL): `count: int; len(count)` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `x007_len_int_realistic.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(count: int) -> int:
    return len(count) if count > 0 else 0


if __name__ == "__main__":
    try:
        r = f(3)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
