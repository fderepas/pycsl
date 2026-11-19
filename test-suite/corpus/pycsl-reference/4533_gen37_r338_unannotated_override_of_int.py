r"""Test 4533 -- gen #37 route #338 (expected FAIL): an UNANNOTATED override (`S.m` returning 0.5) of `B.m -> int`; the base-typed caller `b.m() % 1 == 0` (CPython False for `g(S())`). REFUSED now (R5: a missing return annotation is not a subtype of `int`); FAILED (unproven) before.
"""
# pycsl-expected: FAIL
class B:
    def m(self) -> int:
        return 1

class S(B):
    def m(self):
        return 0.5

#@ ensures \result == True
def g(b: B) -> bool:
    return b.m() % 1 == 0

if __name__ == "__main__":
    assert g(S()) == True
