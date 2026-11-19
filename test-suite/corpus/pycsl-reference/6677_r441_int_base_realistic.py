r"""Test 6677 -- route #441 B1 (expected FAIL): `int(<int>, base)` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `x006_int_base_realistic.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(n: int) -> int:
    return int(n, 16)


if __name__ == "__main__":
    try:
        r = f(255)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
