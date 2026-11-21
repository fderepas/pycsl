r"""Test 3108 — route #278 (expected FAIL, refused): `class B(A): m = lambda self: 2` overrides
`A.m` with a CLASS-BODY BINDING (route #123 gives it no clone, so `B().m()` is contract-free),
but a caller holding an `A`-typed value still used `A.m`'s `== 1` — PROVED under the flag,
CPython 2. The binding now records a pair with no function to check, which is refused
(PYCSL-SUBTYPING-PAIR).
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
    m = lambda self: 2


#@ ensures \result == 1
#@ assigns \nothing
def use(a: A) -> int:
    return a.m()


if __name__ == "__main__":
    print(use(B()))
    assert use(B()) == 2
