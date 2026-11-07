r"""Test 4530 -- gen #37 route #338 (expected FAIL): a base method `-> int` overridden `-> float` (`S.m` returns 0.5), called as `b.m()` on a base-typed parameter: the route #277 refinement goal was `true -> true` (return annotations never compared) and `b.m() % 1 == 0` PROVED (CPython False for `g(S())`). REFUSED now (PYCSL-SEM-OVERRIDE-REFINEMENT, rule R5): an override's return annotation must be a subtype of the base's.
"""
# pycsl-expected: FAIL
class B:
    def m(self) -> int:
        return 1

class S(B):
    def m(self) -> float:
        return 0.5

#@ ensures \result == True
def g_call_override(b: B) -> bool:
    return b.m() % 1 == 0

if __name__ == "__main__":
    assert g_call_override(S()) == True
