r"""Test 4542 -- gen #37 route #338: CONTROL: `B.m -> int` overridden `S.m -> bool` (bool is a subtype of int) is admitted by R5 and the caller PROVES (CPython True). `B` carries a field so it is a record: since route #336 a field-less class is an erased object and `b.m()` is no longer an int.
"""
class B:
    def __init__(self) -> None:
        self.k = 0

    def m(self) -> int:
        return 1

class S(B):
    def m(self) -> bool:
        return True

#@ ensures \result == True
def g(b: B) -> bool:
    return b.m() % 1 == 0

if __name__ == "__main__":
    assert g(S()) == True and g(B()) == True
