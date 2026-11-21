r"""Test 5787 -- gen #37 route #402 (expected FAIL): a frozen `@dataclass R` whose generated `__eq__` compares a field of class `K` with a raising `__eq__`; `{a, b}` (CPython ValueError; PROVED at base 526d534de). REFUSED (PYCSL-R402-UNVERIFIED-EQ: the eq field fixpoint).
"""
# pycsl-expected: FAIL
from dataclasses import dataclass


class K:
    def __init__(self) -> None:
        self.x: int = 1

    #@ no_exception \all
    def __hash__(self) -> int:
        return 0

    def __eq__(self, o: object) -> bool:
        if self.x == 1:
            raise ValueError("e")
        return False


@dataclass(frozen=True)
class R:
    k: K


#@ no_exception \all
def f(a: R, b: R) -> int:
    s = {a, b}
    return 1


if __name__ == "__main__":
    try:
        print("result", f(R(K()), R(K())))
    except Exception as e:
        print("VIOLATION", type(e).__name__, e)
