r"""Test 3103 — route #277 control (PASS by default): `B.m` WEAKENS the precondition
(`k >= -5` vs `k >= 0`) and STRENGTHENS the postcondition (`== k + 1` vs `>= k`), so the
default refinement goal holds and `use(a: A)` keeps its proof — for `A()` and `B()` alike.
"""
# pycsl-expected: PASS


class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ requires k >= 0
    #@ ensures \result >= k
    #@ assigns \nothing
    def m(self, k: int) -> int:
        return k + 3


class B(A):
    #@ requires k >= -5
    #@ ensures \result == k + 1
    #@ assigns \nothing
    def m(self, k: int) -> int:
        return k + 1


#@ requires k >= 0
#@ ensures \result >= k
#@ assigns \nothing
def use(a: A, k: int) -> int:
    return a.m(k)


if __name__ == "__main__":
    assert use(A(), 2) >= 2 and use(B(), 2) >= 2
