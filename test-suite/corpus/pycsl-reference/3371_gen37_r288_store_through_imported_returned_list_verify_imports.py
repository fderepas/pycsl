r"""Test 3371 -- route #288 (expected FAIL): red-team a010: the 3370 shape under --verify-imports (the callee body is verified, the caller still sees a fresh `val`) PROVED; CPython: 5. Now refused.
"""
# pycsl-flags: --verify-imports
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
