r"""Test 4543 -- gen #37 route #338: CONTROL: covariant returns (`-> bool` under `-> int` with contracts, `-> int` under `-> Optional[int]`, `-> AA` under `-> A`) and a contravariant parameter (`Optional[int]` over `int`) are admitted by R5; the base-typed caller PROVES `\result >= 0` from `B.p`'s contract.
"""
from typing import Optional

class A:
    def __init__(self) -> None:
        self.v = 1

class AA(A):
    pass

class B:
    def __init__(self) -> None:
        self.w = 0

    def m(self, x: int) -> Optional[int]:
        return None

    def k(self) -> A:
        return A()

    #@ ensures \result >= 0
    def p(self, x: int) -> int:
        return x * x

class S(B):
    def m(self, x: Optional[int]) -> int:
        return 3

    def k(self) -> AA:
        return AA()

    #@ ensures \result >= 0
    def p(self, x: int) -> bool:
        return True

#@ ensures \result >= 0
def g(b: B, n: int) -> int:
    return b.p(n)

if __name__ == "__main__":
    assert g(S(), 4) >= 0 and g(B(), 4) >= 0
