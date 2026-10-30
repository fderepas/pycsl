r"""Test 7447 -- cv6 D3 (FAIL): route #316/#317 frame of a `\trusted` val. `ys = [1]; g = lambda: ys.__setitem__(0, 7); ys = xs; g()` -- the lambda reads `ys` LATE (at call time, after the alias), so a name read inside a Lambda/generator is never split. Refused upstream (in-place mutation through another name) at base 4d15b89a7 and candidate. CPython f([0]) = 7.
"""
# pycsl-expected: FAIL
from typing import List


#@ \trusted
#@ ensures \result == 0
def k(xs: List[int]) -> int:
    ys = [1]
    g = lambda: ys.__setitem__(0, 7)
    ys = xs
    g()
    return 0


#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
def f(xs: List[int]) -> int:
    k(xs)
    return xs[0]


if __name__ == "__main__":
    print("result", f([0]), "expected 0")
