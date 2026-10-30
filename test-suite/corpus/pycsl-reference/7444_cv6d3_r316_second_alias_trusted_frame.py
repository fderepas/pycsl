r"""Test 7444 -- cv6 D3 (FAIL): route #316/#317 frame of a `\trusted` val. `ys = xs; zs = ys; ys = [0]; zs[0] = 7` -- the top-level rebinding of `ys` does not rebind `zs`, which still holds xs; `writes { xs }` kept. FAILS at base 4d15b89a7 and candidate. CPython f([0]) = 7.
"""
# pycsl-expected: FAIL
from typing import List


#@ \trusted
#@ ensures \result == 0
def k(xs: List[int]) -> int:
    ys = xs
    zs = ys
    ys = [0]
    zs[0] = 7
    return 0


#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
def f(xs: List[int]) -> int:
    k(xs)
    return xs[0]


if __name__ == "__main__":
    print("result", f([0]), "expected 0")
