r"""Test 4573 -- gen #37 route #342: CONTROL: subclass `super().__init__()` then control-flow / `for` stores of NON-invariant fields only; PROVES (CPython 0).
"""
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0

class S(B):
    def __init__(self) -> None:
        super().__init__()
        self.y = 0
        if self.y == 0:
            self.y = 5
        for self.z in range(3):
            pass

#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(S()) == 0
    assert f(B()) == 0
