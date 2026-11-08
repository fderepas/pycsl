r"""Test 6673 -- route #441 B1 (expected FAIL): `n: int; tuple(n)` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `e053_tuple_int.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(n: int) -> int:
    return len(tuple(n))


if __name__ == "__main__":
    try:
        r = f(1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
