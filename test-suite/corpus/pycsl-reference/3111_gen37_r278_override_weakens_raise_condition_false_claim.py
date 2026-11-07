r"""Test 3111 — route #278 (expected FAIL): `A.m` declares `raises ValueError when k > 5`, the
override `B.m` raises it `when k > 3`. `use(a, k)` with `0 <= k <= 5` claims
`no_exception ValueError`: the call-site wrap asserts `not (k > 5)` from the BASE condition,
so it PROVED under the flag — `use(B(), 4)` raises. The goal now carries
`(pre_A /\ k > 3) -> k > 5`, which fails.
"""
# pycsl-expected: FAIL


class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ raises ValueError when k > 5
    def m(self, k: int) -> int:
        if k > 5:
            raise ValueError("a")
        return 0


class B(A):
    #@ ensures \result == 0
    #@ assigns \nothing
    #@ raises ValueError when k > 3
    def m(self, k: int) -> int:
        if k > 3:
            raise ValueError("b")
        return 0


#@ requires 0 <= k <= 5
#@ ensures \result == 0
#@ assigns \nothing
#@ no_exception ValueError
def use(a: A, k: int) -> int:
    return a.m(k)


if __name__ == "__main__":
    try:
        use(B(), 4)
        raise SystemExit("unreachable")
    except ValueError:
        print("ValueError")
