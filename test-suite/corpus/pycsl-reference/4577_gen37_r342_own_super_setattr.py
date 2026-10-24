r"""Test 4577 -- gen #37 route #342 (expected FAIL): NEW latent shape (p1, r341 executor): own `__init__` `super().__setattr__("x", 5)` after `self.x = 0` (no bare `self`; route #150 opacity -> no goal): PROVED (CPython 5). REFUSED (PYCSL-R342-CONSTRUCTOR-STORE-FORM, route #342).
"""
# pycsl-expected: FAIL
#@ class invariant self.x == 0
class B:
    def __init__(self) -> None:
        self.x = 0
        super().__setattr__("x", 5)

#@ ensures \result == 0
def f(b: B) -> int:
    return b.x

if __name__ == "__main__":
    assert f(B()) == 0
