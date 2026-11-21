r"""Test 8563 -- route #544 (control, expected PASS): `isinstance(k, (int, bool))` -- a tuple of classes, no None; CPython returns 0 / 1
"""
# pycsl-expected: PASS
from typing import Union


#@ no_exception \all
def f(k: Union[int, str]) -> int:
    if isinstance(k, (int, bool)):
        return 1
    return 0


if __name__ == "__main__":
    print("result", f("a"), f(3))
