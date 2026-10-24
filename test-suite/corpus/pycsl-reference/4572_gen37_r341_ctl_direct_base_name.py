r"""Test 4572 -- gen #37 route #341: CONTROL: the class header names the base directly (an unrelated alias `Alias = B` exists, used only as a value) and the override keeps `ensures \result == 1`; PROVES (CPython 1) — the #341 advice followed.
"""
class B:
    def __init__(self) -> None:
        self.n = 1
    #@ ensures \result == 1
    def m(self) -> int:
        return 1

Alias = B

class S(B):
    #@ ensures \result == 1
    def m(self) -> int:
        return 1

#@ ensures \result == 1
def g(b: B) -> int:
    return b.m()

if __name__ == "__main__":
    assert g(S()) == 1
    assert g(Alias()) == 1
