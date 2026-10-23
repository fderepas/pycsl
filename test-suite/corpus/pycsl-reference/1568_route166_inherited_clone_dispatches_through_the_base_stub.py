r"""Test 1568 - ROUTE #166 (gen #29): `B(A)` overrides `m` (`\result == 7` vs A's `== 1`); the inherited clone `b__call_m` called the stub `self_m_0` registered first with A's contract, so `B().call_m() == 1` PROVED by default (CPython 7). With per-callee stub names the clone sees B's contract and its own inherited `ensures == 1` fails.
"""
# pycsl-expected: FAIL
_ = 0  # anchor


class A:
    def __init__(self) -> None:
        self.n = 1

    #@ ensures \result == 1
    def m(self) -> int:
        return 1

    #@ ensures \result == 1
    def call_m(self) -> int:
        return self.m()


class B(A):
    #@ ensures \result == 7
    def m(self) -> int:
        return 7


#@ ensures \result == 1
def probe() -> int:
    b = B()
    return b.call_m()

