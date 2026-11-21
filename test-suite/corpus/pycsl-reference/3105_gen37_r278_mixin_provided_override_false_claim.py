r"""Test 3105 — route #278 (expected FAIL): `class B(M, A): pass` — `B().m()` is the FIELDLESS
mixin `M`'s `m` (C3 MRO B, M, A), which returns 2 against `A.m`'s `== 1`. No override pair was
recorded (the pair needed a method DEFINED in `B`, or a clone of it), so `use(a: A) == 1`
PROVED even under `--check-behavioral-subtyping`. CPython: 2. The pair `m__m refines a__m` is
now computed over the MRO and its goal fails.
"""
# pycsl-expected: FAIL


class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


class M:
    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2


class B(M, A):
    pass


#@ ensures \result == 1
#@ assigns \nothing
def use(a: A) -> int:
    return a.m()


if __name__ == "__main__":
    print(use(B()))
    assert use(B()) == 2
