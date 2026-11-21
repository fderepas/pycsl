r"""Test 4531 -- gen #37 route #338 (expected FAIL): #334 residual 6: `self.r = self.m()` with `B.m -> int` overridden `S.m -> float`; the #334 classifier trusted the `-> int` annotation and `b.r % 1 == 0` PROVED (CPython False for `g(S())`). REFUSED now (R5: the override does not keep the base's return annotation).
"""
# pycsl-expected: FAIL
class B:
    def m(self) -> int:
        return 1

    def __init__(self) -> None:
        self.r = self.m()

class S(B):
    def m(self) -> float:
        return 0.5

#@ ensures \result == True
def g_init_override(b: B) -> bool:
    return b.r % 1 == 0

if __name__ == "__main__":
    assert g_init_override(S()) == True
