r"""Test 4460 -- gen #37 route #335 (expected FAIL): witness i33: subclass `@property x` returning 7 shadows the base's invariant field `x` (`invariant self.x == 0`), `S.__init__: pass`; the inherited goal assumed `x = 0` and `f(b: B) -> b.x == 0` PROVED (CPython 7). REFUSED (PYCSL-R335-INHERITED-INVARIANT-CONSTRUCTION, route #335).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0

class S(B):
    def __init__(self) -> None:
        pass
    @property
    def x(self) -> int:
        return 7

#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(S()) == 0, f(S())
