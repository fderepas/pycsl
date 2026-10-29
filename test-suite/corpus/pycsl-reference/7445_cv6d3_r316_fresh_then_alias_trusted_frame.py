r"""Test 7445 -- cv6 D3 (FAIL): route #316/#317 frame of a `\trusted` val. `ys = [0]; ys = xs; ys[0] = 7` -- the LATER top-level rebinding is the alias: the version the store sees is tainted; `writes { xs }` kept. FAILS at base 4d15b89a7 and candidate. CPython f([0]) = 7.
"""
# pycsl-expected: FAIL
from typing import List


#@ \trusted
#@ ensures True
def k(xs: List[int]) -> int:
    ys = [0]
    ys = xs
    ys[0] = 7
    return 0


#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
def f(xs: List[int]) -> int:
    k(xs)
    return xs[0]


if __name__ == "__main__":
    print("result", f([0]), "expected 0")
