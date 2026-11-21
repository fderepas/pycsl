r"""Test 3102 — route #277: 3100's program under `--assume-class-exact` PROVES, as the DECLARED
model assumption CLASS-EXACT (listed by `--soundness-report` with the override pair and the
`a.m(...)` call). CPython: 2 — the claim holds only for exact `A` instances, which is what the
assumption states.
"""
# pycsl-expected: PASS
# pycsl-flags: --assume-class-exact


class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 1
    #@ assigns \nothing
    def m(self) -> int:
        return 1


class B(A):
    #@ assigns \nothing
    def m(self) -> int:
        return 2


#@ ensures \result == 1
#@ assigns \nothing
def use(a: A) -> int:
    return a.m()


if __name__ == "__main__":
    assert use(A()) == 1   # exact instance: the assumption's population
    assert use(B()) == 2   # a subclass instance: outside it
