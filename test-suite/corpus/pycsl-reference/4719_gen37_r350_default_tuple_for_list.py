r"""Test 4719 -- gen #37 route #350 (expected FAIL): `xs: List[int] = (1, 2)` (a tuple display for a list annotation; CPython TypeError on the store). VERIFY-FAIL at base, REFUSED now (route #350).
"""
# pycsl-expected: FAIL
from typing import List
#@ no_exception \all
#@ ensures \result == 5
def f(xs: List[int] = (1, 2)) -> int:  # type: ignore
    xs[0] = 5
    return xs[0]

if __name__ == "__main__":
    print(f())
