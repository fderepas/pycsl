r"""Test 6670 -- route #441 B2 (expected FAIL): `s.startswith(t)` with `t: Tuple[str, bytes]` under `#@ no_exception \all`. PROVED on main f1c249c4e (red team 35 witness `a203_str_startswith_tuple_bytes.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R440-METHOD-NOT-ADMITTED / PYCSL-R441-BUILTIN-SIGNATURE, the signature table of routes #440 / #441).
"""
# pycsl-expected: FAIL
from typing import Any, Dict, List, Optional, Set, Tuple, Union

#@ no_exception \all
def f(s: str, t: Tuple[str, bytes]) -> int:
    return 1 if s.startswith(t) else 0


if __name__ == "__main__":
    try:
        r = f("a", ("b", b"a"))
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
