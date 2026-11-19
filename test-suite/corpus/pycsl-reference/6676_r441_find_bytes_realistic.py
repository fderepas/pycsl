r"""Test 6676 -- route #441 B2 (expected FAIL): a `str.find` of a `bytes` argument under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `x009_find_bytes_realistic.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(s: str, token: bytes) -> int:
    return 1 if s.find(token) >= 0 else 0


if __name__ == "__main__":
    try:
        r = f("abc", b"b")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
