r"""Test 1662 - ROUTE #187 carrier (gen #29): the same hole reached through a module-level METHOD CALL. `counter = Counter(); counter.bump()` (bump `ensures self.n == 3`) followed by a `#@ fresh_globals` driver PROVED `\result == 0` while CPython returns 3 — the call, like every other top-level statement, never reaches the IR.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class Counter:
    #@ assigns self.n
    #@ ensures self.n == 0
    def __init__(self) -> None:
        self.n: int = 0

    #@ assigns self.n
    #@ ensures self.n == 3
    def bump(self) -> int:
        self.n = 3
        return 0


counter = Counter()
counter.bump()


#@ ensures \result == 0
#@ fresh_globals
def probe() -> int:
    return counter.n
