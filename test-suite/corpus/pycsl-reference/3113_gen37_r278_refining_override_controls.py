r"""Test 3113 — route #278 controls (PASS by default): overrides that DO refine their base on
every axis the check now covers — `B.m` claims `no_exception \all` and assigns nothing
(the base may raise `ValueError when k > 5`); `C.m` raises
`ValueError when k > 7` (stronger than `k > 5`); `D.m` writes `self.w`, a field `A` does not
have (no `A`-typed receiver can observe it). Every refinement goal is emitted by default and
proves; no override is refused. (A caller `use(a: A, k)` is not included: a call to a method
declaring `raises` through a parameter receiver does not carry its `ensures` today — a
pre-existing incompleteness, fail-closed, independent of this route.)
"""
# pycsl-expected: PASS


class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ requires k >= 0
    #@ ensures \result == 1
    #@ assigns \nothing
    #@ raises ValueError when k > 5
    def m(self, k: int) -> int:
        if k > 5:
            raise ValueError("a")
        return 1


class B(A):
    #@ ensures \result == 1
    #@ assigns \nothing
    #@ no_exception \all
    def m(self, k: int) -> int:
        return 1


class C(A):
    #@ ensures \result == 1
    #@ assigns \nothing
    #@ raises ValueError when k > 7
    def m(self, k: int) -> int:
        if k > 7:
            raise ValueError("c")
        return 1


class D(A):
    def __init__(self) -> None:
        self.v: int = 0
        self.w: int = 0

    #@ ensures \result == 1
    #@ assigns self.w
    def m(self, k: int) -> int:
        self.w = 3
        return 1


if __name__ == "__main__":
    for o in (A(), B(), C(), D()):
        assert o.m(5) == 1   # every override honours A.m's contract at k = 5
