r"""Test 8401 -- route #523 (control, expected PASS): a local str TUPLE literal (immutable) bound once may also be read outside a `for` (here `len(a)`); its loop keeps the literal materialisation and `ensures \result == 0` proves; CPython returns 0
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional, Tuple


#@ ensures \result == 0
def f(k: int) -> int:
    a = ("abc", "defg")
    n = len(a)
    for p in a:
        if p == "z":
            return 1
    return n - 2


if __name__ == "__main__":
    print("result", f(0))
