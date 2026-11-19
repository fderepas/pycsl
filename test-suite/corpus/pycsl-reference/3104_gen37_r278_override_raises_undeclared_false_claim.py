r"""Test 3104 — route #278 (expected FAIL, refused): `B.m` raises a `ValueError` that `A.m` does
not declare; `use(a: A)` claims `no_exception \all` over `a.m()`. Even WITH
`--check-behavioral-subtyping` it PROVED (the goal compared requires/ensures only; route
#272's hidden-raise rule resolves `a.m()` by the static type) — CPython raises ValueError.
Now an override may only raise what the base declares (PYCSL-SEM-OVERRIDE-REFINEMENT).
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
    #@ assigns \nothing
    def m(self) -> int:
        if self.v == 0:
            raise ValueError("x")
        return 1


#@ ensures \result == 1
#@ assigns \nothing
#@ no_exception \all
def use(a: A) -> int:
    return a.m()


if __name__ == "__main__":
    try:
        use(B())
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
