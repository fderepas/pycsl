r"""Test 1371 — ROUTE #132 (class arm): `class K: N = 3; N += 2`; `self.N` was folded to 3 and `K.get` PROVED `\result == 3` while CPython returns 5.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class K:
    N = 3
    N += 2

    def __init__(self) -> None:
        self.a = 0

    #@ ensures \result == 3
    #@ assigns \nothing
    def get(self) -> int:
        return self.N
