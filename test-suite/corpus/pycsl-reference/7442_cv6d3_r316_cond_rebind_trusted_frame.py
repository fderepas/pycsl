r"""Test 7442 -- cv6 D3 (FAIL): route #316/#317 frame of a `\trusted` val. `ys = xs; if c: ys = [0]; ys.append(1); ys[0] = 7` -- the rebinding is CONDITIONAL, so `ys` may still be `xs` at the store: the statement-level SSA split (a top-level rebinding starts a new version) leaves the nested rebinding inside the alias version, the inferred frame keeps `writes { xs }`, and the caller cannot prove `xs[0]` unchanged. FAILS at base 4d15b89a7 and candidate. CPython f([0]) = 7.
"""
# pycsl-expected: FAIL
from typing import List


#@ \trusted
#@ ensures True
def k(c: bool, xs: List[int]) -> int:
    ys = xs
    if c:
        ys = [0]
    ys.append(1)
    ys[0] = 7
    return len(ys)


#@ requires len(xs) >= 1 and xs[0] == 0
#@ ensures \result == 0
def f(xs: List[int]) -> int:
    k(False, xs)
    return xs[0]


if __name__ == "__main__":
    print("result", f([0]))
