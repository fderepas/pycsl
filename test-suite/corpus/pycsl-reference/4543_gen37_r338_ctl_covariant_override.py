r"""Test 4543 -- gen #37 route #338: CONTROL: covariant returns (`Optional[int]` -> `int`, `A` -> `AA(A)`) and a contravariant parameter (`int` -> `Optional[int]`) are admitted by R5; PROVES.
"""
from typing import Optional

class A:
    def __init__(self) -> None:
        self.v = 1

class AA(A):
    pass

class B:
    def m(self, x: int) -> Optional[int]:
        return None

    def k(self) -> A:
        return A()

class S(B):
    def m(self, x: Optional[int]) -> int:
        return 3

    def k(self) -> AA:
        return AA()

#@ ensures \result == 1
def g(b: B) -> int:
    a = b.k()
    return 1

if __name__ == "__main__":
    assert g(S()) == 1 and g(B()) == 1
