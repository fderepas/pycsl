r"""Test 3112 — route #278 (expected FAIL, refused): `A.get` claims `no_exception \all`; the
override `B.get` indexes without that claim (CPython IndexError for `k = 9`). Under
`--strict-no-exception-propagation` a caller trusts the BASE's `no_exception` for a call it
cannot see into, so the override must keep the base's `no_exception` set. COVERAGE: this
caller was already refused by the implicit-raise rule (it sees `b__get`'s subscript); the
override itself is now refused first (rule R2), independent of any caller.
"""
# pycsl-expected: FAIL
# pycsl-flags: --strict-no-exception-propagation
from typing import List


class A:
    def __init__(self) -> None:
        self.v: int = 0

    #@ ensures \result == 0
    #@ assigns \nothing
    #@ no_exception \all
    def get(self, xs: List[int], k: int) -> int:
        return 0


class B(A):
    #@ ensures \result == 0
    #@ assigns \nothing
    def get(self, xs: List[int], k: int) -> int:
        return xs[k] * 0


#@ ensures \result == 0
#@ assigns \nothing
#@ no_exception \all
def use(a: A, xs: List[int], k: int) -> int:
    return a.get(xs, k)


if __name__ == "__main__":
    try:
        use(B(), [1], 9)
        raise SystemExit("unreachable")
    except IndexError:
        print("IndexError")
