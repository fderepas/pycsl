r"""Test 8565 -- route #545 (control, expected PASS): `n += v` of an `Optional[int]` parameter after an early return on None; CPython returns 1 / 7
"""
# pycsl-expected: PASS
from typing import Optional


#@ no_exception \all
def f(n: int, v: Optional[int]) -> int:
    if v is None:
        return n
    n += v
    return n


if __name__ == "__main__":
    print("result", f(1, None), f(2, 5))
