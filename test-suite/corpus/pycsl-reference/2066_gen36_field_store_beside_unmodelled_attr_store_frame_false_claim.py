r"""Test 2066 — gen #36 (expected FAIL): FRAME twin of 2064 — the widened `writes` must not
let the field be treated as preserved: from `n == 5`, `mark()` leaves `n == 1` (CPython), so
`self.n == \old(self.n)` must NOT prove.
"""
# pycsl-expected: FAIL


class Acc:
    def __init__(self) -> None:
        self.n: int = 0

    #@ requires self.n == 5
    #@ ensures self.n == \old(self.n)
    #@ assigns self.n, self.tag
    def mark(self) -> None:
        self.n = 1
        self.tag = 7
