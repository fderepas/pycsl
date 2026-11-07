r"""Test 8564 -- route #545 (control, expected PASS): `-v` of an `Optional[int]` parameter after `if v is None: return 0`; CPython returns 0 / -3
"""
# pycsl-expected: PASS
from typing import Optional


#@ no_exception \all
def f(v: Optional[int]) -> int:
    if v is None:
        return 0
    return -v


if __name__ == "__main__":
    print("result", f(None), f(3))
