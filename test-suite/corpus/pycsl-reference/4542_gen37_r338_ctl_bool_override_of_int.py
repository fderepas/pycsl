r"""Test 4542 -- gen #37 route #338: CONTROL: `B.m -> int` overridden `S.m -> bool` (bool is a subtype of int) is admitted by R5 and the caller PROVES (CPython True).
"""
class B:
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
