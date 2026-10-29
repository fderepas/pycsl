r"""Test 7443 -- cv6 D3 (FAIL): route #316/#317 frame of a `\trusted` val. `ys = [1]; for ..: ys[0] = 7; ys = xs` -- the alias assignment is inside a LOOP (second iteration stores into xs). The loop is ONE top-level statement, so it stays in the version started by `ys = [1]`, which the alias taints; `writes { xs }` kept. FAILS at base 4d15b89a7 and candidate. CPython f([0]) = 7.
"""
# pycsl-expected: FAIL
from typing import List


#@ \trusted
#@ ensures True
def k(xs: List[int]) -> int:
    ys = [1]
    for i in range(2):
        ys[0] = 7
        ys = xs
    return 0


#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
def f(xs: List[int]) -> int:
    k(xs)
    return xs[0]


if __name__ == "__main__":
    print("result", f([0]), "expected 0")
