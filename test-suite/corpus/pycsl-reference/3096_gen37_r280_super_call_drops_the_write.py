r"""Test 3096 — route #280 (expected FAIL): `super().bump()` in an override declared `assigns \nothing`
with `self.v == \old(self.v)`: the base `bump` writes `self.v`, and the super-call receiver is a
computed `super()` call, so the write vanished and the override PROVED at 72ab1c57 (census
probe q30). CPython: `v` becomes 1. Now refused.
"""
# pycsl-expected: FAIL
class B:
    def __init__(self) -> None:
        self.v: int = 0

    #@ assigns self.v
    def bump(self) -> None:
        self.v = self.v + 1


class D(B):
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures self.v == \old(self.v)
    #@ assigns \nothing
    def go(self) -> None:
        super().bump()


if __name__ == "__main__":
    d = D()
    d.go()
    assert d.v == 1
