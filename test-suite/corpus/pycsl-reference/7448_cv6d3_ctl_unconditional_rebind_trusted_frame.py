r"""Test 7448 -- cv6 D3 (PASS): CONTROL -- `ys = xs; ys = [0]; ys[0] = 7` in a `\trusted` val: the top-level, unconditional rebinding to a fresh list means the store never reaches xs. At base 4d15b89a7 the flow-insensitive alias analysis charged it to xs (`writes { xs }`, caller FAILED to prove `xs[0]` unchanged; the same false charge is the PYCSL-METHOD-FRAME refusal of the mirror port of `_Unparser._str_literal_helper`). Now no `writes`, PROVED; CPython f([0]) = 0.
"""
# pycsl-expected: PASS
from typing import List


#@ \trusted
def k(xs: List[int]) -> int:
    ys = xs
    ys = [0]
    ys[0] = 7
    return 0


#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
def f(xs: List[int]) -> int:
    k(xs)
    return xs[0]


if __name__ == "__main__":
    print("result", f([0]), "expected 0")
