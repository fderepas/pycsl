r"""Test 8773 -- route #564 (control, expected PASS): tuple / set displays whose elements CPython evaluates: an int ordering, a str ordering, unary `-` of an int, `str + str`, a str needle in a str; CPython 1
"""
# pycsl-expected: PASS
from typing import List


#@ ensures \result == 1
def f(k: int, t: str, xs: List[int]) -> int:
    w = (1, k < 2)
    v = (1, -k)
    u = {1, k + 1}
    q = (1, t + t)
    r = (1, "a" in t)
    z = (1, t < "b")
    return w[0]


if __name__ == "__main__":
    print(f(1, "ab", [1, 2]))
