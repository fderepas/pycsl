r"""Test 6954 -- route #449 (expected FAIL): `total(items, start=1)` over `def total(items, initial=0)` (the unknown keyword was dropped and the default used). PROVED on main db6c57253 (red team 36 witness `c12_u025_realistic_kw.py`); CPython raises TypeError (the `__main__` driver prints VIOLATION). Now REFUSED (PYCSL-R449-CALL-SIGNATURE).
"""
# pycsl-expected: FAIL
from typing import List


def total(items: List[int], initial: int = 0) -> int:
    s = initial
    for x in items:
        s += x
    return s


#@ no_exception \all
def f(items: List[int]) -> int:
    return total(items, start=1)


if __name__ == "__main__":
    try:
        r = f([1])
        print("result", r)
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
