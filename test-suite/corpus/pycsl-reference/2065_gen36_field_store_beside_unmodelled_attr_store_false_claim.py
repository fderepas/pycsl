r"""Test 2065 — gen #36 (expected FAIL): NON-VACUITY twin of 2064 — after `mark()` the field
is 1 (CPython: `a.n == 1`), so `self.n == 0` must NOT prove.
"""
# pycsl-expected: FAIL


class Acc:
    def __init__(self) -> None:
        self.n: int = 0

    #@ ensures self.n == 0
    #@ assigns self.n, self.tag
    def mark(self) -> None:
        self.n = 1
        self.tag = 7
