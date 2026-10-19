r"""Test 3109 — route #278 (expected FAIL, refused): `A.m` declares `assigns \nothing`, the
override `B.m` writes `self.v` (an `A` field) and declares it. A caller holding `a: A` keeps
`a.v == 0` across `a.m()` by `A.m`'s frame, so `use(B()) == 0` PROVED under the flag while
CPython returns 5. An override may only assign what the base declares (a field the base
class does not have is exempt — no base-typed receiver can see it).
"""
# pycsl-expected: FAIL


class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


class B(A):
    #@ ensures \result == 1
    #@ assigns self.v
    def m(self) -> int:
        self.v = 5
        return 1


#@ requires a.v == 0
#@ ensures \result == 0
#@ assigns a.v
def use(a: A) -> int:
    a.m()
    return a.v


if __name__ == "__main__":
    print(use(B()))
    assert use(B()) == 5
