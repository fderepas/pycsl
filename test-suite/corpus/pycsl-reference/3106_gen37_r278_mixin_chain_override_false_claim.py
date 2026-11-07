r"""Test 3106 — route #278 (expected FAIL): 3105 through one more level, `B(M, A)` with `M(N)` and
`N.m` returning 2: the provider is two bases away from `B`. PROVED with the flag before; the
MRO pair `n__m refines a__m` now fails. CPython: 2.
"""
# pycsl-expected: FAIL


class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


class N:
    #@ ensures \result == 2
    #@ assigns \nothing
    def m(self) -> int:
        return 2


class M(N):
    pass


class B(M, A):
    pass


#@ ensures \result == 1
#@ assigns \nothing
def use(a: A) -> int:
    return a.m()


if __name__ == "__main__":
    print(use(B()))
    assert use(B()) == 2
