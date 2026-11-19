r"""Test 4574 -- gen #37 route #342: CONTROL: top-level `self.x = k` under `requires k >= 0` plus `type(self).__name__` (a read of `self`); PROVES — the #342 advice followed.
"""
#@ class invariant self.x >= 0
class B:
    #@ requires k >= 0
    def __init__(self, k: int) -> None:
        self.x = k
        self.tag = type(self).__name__

#@ ensures \result >= 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B(4)) >= 0
