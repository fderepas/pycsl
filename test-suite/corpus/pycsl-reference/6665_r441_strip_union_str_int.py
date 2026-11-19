r"""Test 6665 -- route #441 B2 (expected FAIL): `s.strip(t)` with `t: Union[str, int]` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `m007_strip_int.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(s: str, t: Union[str, int]) -> int:
    return len(s.strip(t))


if __name__ == "__main__":
    try:
        r = f("a", 1)
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
