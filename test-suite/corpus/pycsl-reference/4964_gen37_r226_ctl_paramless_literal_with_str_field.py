r"""Test 4964 -- gen #37 route #226: CONTROL for 4955: the same paramless constructor with `self.n = 7` (the invariant `self.n >= 5` HOLDS); the projection states `forall n. n = 7 -> n >= 5` and the file PROVES (CPython 7).
"""
#@ class invariant self.n >= 5
class C:
    def __init__(self) -> None:
        self.n = 7
        self.name: str = "a"

#@ ensures \result >= 5
def read(c: C) -> int:
    return c.n

if __name__ == "__main__":
    assert read(C()) == 7
