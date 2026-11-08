r"""Test 8400 -- route #523 (control, expected PASS): a local str list literal bound once at the top of the body and read only as a `for` iterable keeps the faithful literal materialisation: the early `return 1` on "z" is dead, `ensures \result == 0` proves; CPython returns 0
"""
# pycsl-expected: PASS
from typing import Any, Dict, List, Optional


#@ ensures \result == 0
def f(k: int) -> int:
    a = ["abc", "defg"]
    for p in a:
        if p == "z":
            return 1
    return 0


if __name__ == "__main__":
    print("result", f(0))
