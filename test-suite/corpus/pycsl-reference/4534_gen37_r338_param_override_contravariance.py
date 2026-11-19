r"""Test 4534 -- gen #37 route #338 (expected FAIL): an override NARROWING a parameter annotation (`B.m(x: int)` overridden `S.m(x: bool)`; the base-typed caller passes 5). REFUSED now (R5: parameter annotations are contravariant); FAILED (unproven) before.
"""
# pycsl-expected: FAIL
class B:
    #@ requires x >= 0
    #@ ensures \result >= 0
    def m(self, x: int) -> int:
        return x

class S(B):
    #@ ensures \result == 7
    def m(self, x: bool) -> int:
        return 7 if x <= 1 else -1

#@ ensures \result >= 0
def g(b: B) -> int:
    return b.m(5)

if __name__ == "__main__":
    assert g(S()) >= 0
