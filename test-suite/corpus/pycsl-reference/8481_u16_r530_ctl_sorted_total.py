r"""Test 8481 -- route #530 (control, expected PASS): `sorted` over elements with a total order, or with a key total on them, stays a field initialiser: `sorted(xs)` of a List[int], `sorted(ws, key=len)` of a List[str], `sorted(xs, reverse=True)`; CPython f([3, 1], ["bb", "a"]) returns 1
"""
# pycsl-expected: PASS
from typing import List


class C:
    def __init__(self, xs: List[int], ws: List[str]) -> None:
        self.a = sorted(xs)
        self.b = sorted(ws, key=len)
        self.c = sorted(xs, reverse=True)


#@ no_exception \all
#@ ensures \result == 1
def f(xs: List[int], ws: List[str]) -> int:
    c = C(xs, ws)
    return 1


if __name__ == "__main__":
    print(f([3, 1], ["bb", "a"]))
