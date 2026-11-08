r"""Test 7443 -- cv6 D3 (FAIL): route #316 frame of a METHOD (PYCSL-METHOD-FRAME). `ys = [1]; for ..: ys[0] = 7; ys = xs` under `#@ assigns \nothing` -- the alias assignment is inside a LOOP (the second iteration stores into xs). The loop is ONE top-level statement, so it stays in the version started by `ys = [1]`, which the alias taints: still REFUSED. REFUSED at base 4d15b89a7 and candidate. CPython: xs[0] becomes 7.
"""
# pycsl-expected: FAIL
from typing import List


class U:
    def __init__(self) -> None:
        self.n: int = 0

    #@ requires len(xs) >= 1
    #@ ensures \result == 7
    #@ assigns \nothing
    def h(self, xs: List[int]) -> int:
        ys = [1]
        for i in range(2):
            ys[0] = 7
            ys = xs
        return ys[0]


if __name__ == "__main__":
    a = [0]
    U().h(a)
    print("xs[0] after", a[0], "VIOLATION of assigns \\nothing" if a[0] != 0 else "")
