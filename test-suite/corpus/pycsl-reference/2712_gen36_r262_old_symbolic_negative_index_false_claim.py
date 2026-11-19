r"""Test 2712 — route #262 (expected FAIL): `\old(xs[k])` with symbolic `k == -1` — the
same raw cell inside `old` — PROVED `\old(xs[k]) == xs[k]` at b35d9c5e. CPython: 0 != 7.
"""
# pycsl-expected: FAIL
from typing import List


#@ requires len(xs) == 2 and k == -1
#@ requires xs[1] == 0
#@ ensures \old(xs[k]) == xs[k]
#@ assigns xs[1]
def f(xs: List[int], k: int) -> None:
    xs[1] = 7


if __name__ == "__main__":
    xs = [0, 0]
    f(xs, -1)
    assert xs[-1] == 7
