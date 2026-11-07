r"""Test 3370 -- route #288 (expected FAIL): red-team a009: `b = ident2(a); b[0] = 5; return a[0]` with an IMPORTED `ident2` (a `val` with a FRESH result) PROVED `\result == 1`; CPython: 5. Now refused (PYCSL-M6-MUTATION-THROUGH-RETURNED-ALIAS).
"""
# pycsl-expected: FAIL
from typing import List
from multi_file_lib.r288_ident import ident2


#@ ensures \result == 1
def f() -> int:
    a: List[int] = [1]
    b: List[int] = ident2(a)
    b[0] = 5
    return a[0]


if __name__ == "__main__":
    assert f() == 5
