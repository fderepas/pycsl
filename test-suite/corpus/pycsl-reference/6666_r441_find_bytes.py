r"""Test 6666 -- route #441 B2 (expected FAIL): `s.find(t)` with `t: bytes` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `a021_str_find_bytes.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(s: str, t: bytes) -> int:
    return s.find(t)


if __name__ == "__main__":
    try:
        r = f("a", b"a")
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
