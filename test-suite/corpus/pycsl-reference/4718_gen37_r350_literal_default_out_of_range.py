r"""Test 4718 -- gen #37 route #350 (expected FAIL): `def f(x: Literal[1, 2] = 3)` PROVED `\result == 1 or \result == 2` (CPython 3). REFUSED now (route #350).
"""
# pycsl-expected: FAIL
from typing import Literal
#@ ensures \result == 1 or \result == 2
def f(x: Literal[1, 2] = 3) -> int:  # type: ignore
    return x

if __name__ == "__main__":
    print(f())
