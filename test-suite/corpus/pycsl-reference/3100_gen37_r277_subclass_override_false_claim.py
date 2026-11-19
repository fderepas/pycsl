r"""Test 3100 — route #277 (expected FAIL): `use(a: A)` claims `\result == 1` over `a.m()`;
`B(A).m` returns 2 and states nothing. The caller is verified against `A.m`'s contract, and
the override's refinement of it used to be checked only under `--check-behavioral-subtyping`
(undeclared CLASS-EXACT assumption) — PROVED, CPython 2. The check is now the default: the
goal `b__m_refines_a` fails.
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
    #@ assigns \nothing
    def m(self) -> int:
        return 2


#@ ensures \result == 1
#@ assigns \nothing
def use(a: A) -> int:
    return a.m()


if __name__ == "__main__":
    print(use(B()))
    assert use(B()) == 2  # CPython: the override runs; the claim `== 1` is false
