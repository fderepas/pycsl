r"""Test 6694 -- routes #440 / #441 (expected PASS): CONTROL: a `Union[str, int]` receiver narrowed by `isinstance(x, str)` admits `x.upper()`, and the result of `w = y.strip()` on an `Optional[str]` narrowed by `is not None` is DERIVED `str` (a call returns only on a non-`None` receiver), so `len(w.upper())` matches `len`'s row, under `#@ no_exception \all`. PROVED at candidate (CPython ok).
"""
# pycsl-expected: PASS
from typing import Optional, Union


#@ no_exception \all
def f(x: Union[str, int], y: Optional[str]) -> int:
    a = 0
    if isinstance(x, str):
        a = len(x.upper())
    if y is not None:
        w = y.strip()
        a = a + len(w.upper())
    return a


if __name__ == "__main__":
    print(f("ab", " c "), f(3, None))
